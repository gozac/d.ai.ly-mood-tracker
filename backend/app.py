from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import json
from flask import Flask, request, jsonify

from models import User, Report, Evaluation, Goal, Base, db_session
from database import init_db
from ai_service import generate_summary, generate_evaluation
from config import Config

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configuration sécurité
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modèles Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str
    user: str

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

class ReportCreate(BaseModel):
    answers: dict

class GoalCreate(BaseModel):
    objective: dict

# Modèles Pydantic additionnels
class AdviseCreate(BaseModel):
    advisor: int

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

# Fonctions utilitaires
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + Config.JWT_ACCESS_TOKEN_EXPIRES
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, Config.JWT_SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = User.get(int(user_id))
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/register", response_model=dict)
async def register(user: UserCreate):
    # Hasher le mot de passe avec la nouvelle configuration
    # hashed_password = pwd_context.hash(user.password)
    if User.create(user.username, user.password):
        return {"message": "User created successfully", "user": user.username}
    raise HTTPException(status_code=409, detail="Username already exists")

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.get_by_username(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        if not User.verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        print(f"Password verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"user": user.username, "access_token": access_token, "token_type": "bearer"}

@app.post("/message")
async def message(message: str):
    return {"message": message}

@app.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    return {
        "message": "Token is valid",
        "user": {
            "id": current_user.id,
            "username": current_user.username
        }
    }

@app.post("/submit-report")
async def submit_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user)
):
    today = datetime.now().strftime('%Y-%m-%d')

    # Récupérer les objectifs actifs
    goals = db_session.query(Goal).filter_by(
        user_id=current_user.id, 
        status='active'
    ).all()
    
    summary = generate_summary(report.answers, [goal.title for goal in goals])
    
    new_report = Report(
        user_id=current_user.id,
        date=today,
        answers=json.dumps(report.answers),
        summary=summary
    )
    
    try:
        db_session.add(new_report)
        db_session.commit()
        return {
            "message": "Report submitted successfully",
            "summary": summary
        }
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/create-advise", response_model=dict)
async def create_advise(
    advise: AdviseCreate,
    current_user: User = Depends(get_current_user)
):
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Récupérer les 10 derniers rapports
    reports = db_session.query(Report)\
        .filter_by(user_id=current_user.id)\
        .order_by(Report.date.desc())\
        .limit(10)\
        .all()
    
    evaluation = generate_evaluation(
        [f"{r.summary}{r.date}" for r in reports], 
        advise.advisor
    )
    
    # Supprimer l'ancienne évaluation et créer la nouvelle
    db_session.query(Evaluation).filter_by(user_id=current_user.id).delete()
    
    new_evaluation = Evaluation(
        user_id=current_user.id,
        date=today,
        content=evaluation
    )
    
    try:
        db_session.add(new_evaluation)
        db_session.commit()
        return {
            "message": "Evaluation created successfully",
            "evaluation": evaluation
        }
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/get-today-report", response_model=dict)
async def get_today_report(current_user: User = Depends(get_current_user)):
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Modification de la requête pour faire un LEFT JOIN correct
    report = db_session.query(Report, Evaluation)\
        .outerjoin(Evaluation, Report.user_id == Evaluation.user_id)\
        .filter(Report.user_id == current_user.id)\
        .filter(Report.date == today)\
        .first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for today"
        )
    
    # Déballage des résultats
    report_obj, evaluation_obj = report
    
    return {
        "date": report_obj.date,
        "answers": json.loads(report_obj.answers) if hasattr(report_obj, 'answers') else None,
        "summary": report_obj.summary,
        "evaluation": evaluation_obj.content if evaluation_obj else None
    }

@app.post("/add-goal", response_model=dict)
async def add_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_user)
):
    title = goal.objective.get('title')
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal title is required"
        )
    
    new_goal = Goal(
        user_id=current_user.id,
        title=title,
        status='active'
    )
    
    try:
        db_session.add(new_goal)
        db_session.commit()
        
        return {
            "message": "Goal added successfully",
            "goal": {
                "id": new_goal.id,
                "title": title,
                "status": "active"
            }
        }
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/get-goals", response_model=list)
async def get_goals(
    status: str = "active",
    current_user: User = Depends(get_current_user)
):
    goals = db_session.query(Goal)\
        .filter_by(user_id=current_user.id)\
        .filter_by(status=status)\
        .all()
    
    return [{
        "id": goal.id,
        "title": goal.title,
        "status": goal.status,
    } for goal in goals]

@app.put("/update-goal/{goal_id}", response_model=dict)
async def update_goal(
    goal_id: int,
    goal: GoalUpdate,
    current_user: User = Depends(get_current_user)
):
    db_goal = db_session.query(Goal)\
        .filter_by(id=goal_id)\
        .filter_by(user_id=current_user.id)\
        .first()
    
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    title = goal.title or db_goal.title
    status = goal.status or db_goal.status
    
    try:
        db_goal.title = title
        db_goal.status = status
        db_session.commit()
        
        return {
            "message": "Goal updated successfully",
            "goal": {
                "id": db_goal.id,
                "title": title,
                "status": status
            }
        }
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/delete-goal/{goal_id}", response_model=dict)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user)
):
    db_goal = db_session.query(Goal)\
        .filter_by(id=goal_id)\
        .filter_by(user_id=current_user.id)\
        .first()
    
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or not authorized"
        )
    
    try:
        db_session.delete(db_goal)
        db_session.commit()
        return {"message": "Goal deleted successfully"}
    except Exception as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.on_event("shutdown")
async def shutdown_event():
    db_session.remove()

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)