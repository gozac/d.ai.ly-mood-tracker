from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import sqlite3
import json

from models import User
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
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE username = ?', (form_data.username,)).fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        if not pwd_context.verify(form_data.password, user[2]):
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
    
    access_token = create_access_token(data={"sub": str(user[0])})
    return {"user": user[1], "access_token": access_token, "token_type": "bearer"}

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
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')

    goals = c.execute(
        'SELECT title FROM goals WHERE user_id = ? AND status = ?', 
        (current_user.id, 'active')
    ).fetchall()
    
    summary = generate_summary(report.answers, goals)
    
    c.execute(
        'INSERT INTO reports (user_id, date, answers, summary) VALUES (?, ?, ?, ?)',
        (current_user.id, today, json.dumps(report.answers), summary)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Report submitted successfully",
        "summary": summary
    }

@app.post("/create-advise", response_model=dict)
async def create_advise(
    advise: AdviseCreate,
    current_user: User = Depends(get_current_user)
):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    reports = c.execute(
        'SELECT summary, date FROM reports WHERE user_id = ? ORDER BY date DESC LIMIT 10',
        (current_user.id,)
    ).fetchall()
    
    evaluation = generate_evaluation([r[0] + r[1] for r in reports], advise.advisor)
    
    c.execute('DELETE FROM evaluations WHERE user_id = ?', (current_user.id,))
    c.execute(
        'INSERT INTO evaluations (user_id, date, content) VALUES (?, ?, ?)',
        (current_user.id, today, evaluation)
    )
    
    conn.commit()
    conn.close()
    
    return {
        "message": "Evaluation created successfully",
        "evaluation": evaluation
    }

@app.get("/get-today-report", response_model=dict)
async def get_today_report(current_user: User = Depends(get_current_user)):
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    report = c.execute(
        '''SELECT r.answers, r.summary, e.content, r.date 
           FROM reports r 
           LEFT JOIN evaluations e ON e.user_id = r.user_id 
           WHERE r.user_id = ? AND r.date = ?''',
        (current_user.id, today)
    ).fetchone()
    
    conn.close()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for today"
        )
    
    return {
        "date": report[3],
        "answers": json.loads(report[0]),
        "summary": report[1],
        "evaluation": report[2]
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
    
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    try:
        c.execute(
            'INSERT INTO goals (user_id, title) VALUES (?, ?)',
            (current_user.id, title)
        )
        goal_id = c.lastrowid
        conn.commit()
        
        return {
            "message": "Goal added successfully",
            "goal": {
                "id": goal_id,
                "title": title,
                "status": "active"
            }
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        conn.close()

@app.get("/get-goals", response_model=list)
async def get_goals(
    status: str = "active",
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    goals = c.execute(
        'SELECT id, title, status FROM goals WHERE user_id = ? AND status = ?', 
        (current_user.id, status)
    ).fetchall()
    
    conn.close()
    
    return [{
        "id": goal[0],
        "title": goal[1],
        "status": goal[2],
    } for goal in goals]

@app.put("/update-goal/{goal_id}", response_model=dict)
async def update_goal(
    goal_id: int,
    goal: GoalUpdate,
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    db_goal = c.execute(
        'SELECT * FROM goals WHERE id = ? AND user_id = ?', 
        (goal_id, current_user.id)
    ).fetchone()
    
    if not db_goal:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    title = goal.title or db_goal[2]
    status = goal.status or db_goal[4]
    
    try:
        c.execute(
            'UPDATE goals SET title = ?, status = ? WHERE id = ?',
            (title, status, goal_id)
        )
        conn.commit()
        
        return {
            "message": "Goal updated successfully",
            "goal": {
                "id": goal_id,
                "title": title,
                "status": status
            }
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        conn.close()

@app.delete("/delete-goal/{goal_id}", response_model=dict)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user)
):
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    try:
        c.execute(
            'DELETE FROM goals WHERE id = ? AND user_id = ?',
            (goal_id, current_user.id)
        )
        
        if c.rowcount == 0:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found or not authorized"
            )
        
        conn.commit()
        return {"message": "Goal deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)