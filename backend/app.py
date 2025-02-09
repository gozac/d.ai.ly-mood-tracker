from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash
from models import User
from database import init_db
from ai_service import generate_summary, generate_evaluation
import sqlite3, json
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)

jwt = JWTManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    
    user = User.create(username, password)
    if user:
        access_token = create_access_token(identity=user[0])
        return jsonify({
            "message": "User created successfully",
            "token": access_token,
            "user": {
                "id": user[0],
                "username": user[1]
            }
            }), 201
    else:
        return jsonify({"error": "Username already exists"}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user[2], password):
        user_obj = User(user[0], user[1], user[2])
        login_user(user_obj)
        # Créer le token JWT
        access_token = create_access_token(identity=user[0])

        return jsonify({
            "message": "Logged in successfully",
            "token": access_token,
            "user": {
                "id": user[0],
                "username": user[1]
            }
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/verify-token", methods=["GET"])
@jwt_required()
def verify_token():
    current_user_id = get_jwt_identity()
    
    # Récupérer les informations de l'utilisateur depuis la base de données
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE id = ?', (current_user_id,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "message": "Token is valid",
        "user": {
            "id": user[0],
            "username": user[1]
        }
    }), 200

@app.route("/refresh-token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({"token": new_token}), 200

@app.route("/submit-report", methods=["POST"])
@login_required
def submit_report():
    data = request.json
    answers = data.get('answers')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Générer le résumé avec OpenAI
    summary = generate_summary(answers)
    
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    # Sauvegarder le rapport
    c.execute(
        'INSERT INTO reports (user_id, date, answers, summary) VALUES (?, ?, ?, ?)',
        (current_user.id, today, json.dumps(answers), summary)
    )
    
    # Récupérer l'historique des rapports
    reports = c.execute(
        'SELECT summary FROM reports WHERE user_id = ? ORDER BY date DESC LIMIT 7',
        (current_user.id,)
    ).fetchall()
    
    # Générer l'évaluation
    evaluation = generate_evaluation([r[0] for r in reports])
    
    # Mettre à jour l'évaluation
    c.execute('DELETE FROM evaluations WHERE user_id = ?', (current_user.id,))
    c.execute(
        'INSERT INTO evaluations (user_id, date, content) VALUES (?, ?, ?)',
        (current_user.id, today, evaluation)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Report submitted successfully",
        "summary": summary,
        "evaluation": evaluation
    }), 201

@app.route("/get-today-report", methods=["GET"])
@login_required
def get_today_report():
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
    
    if report:
        return jsonify({
            "date": report[3],
            "answers": json.loads(report[0]),
            "summary": report[1],
            "evaluation": report[2]
        }), 200
    
    return jsonify({"message": "No report found for today"}), 404

@app.route("/add-goal", methods=["POST"])
@login_required
def add_goal():
    data = request.json
    objective = data.get('objective')
    title = objective.get('title')
    
    if not title:
        return jsonify({"error": "Goal title is required"}), 400
    
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    try:
        c.execute(
            'INSERT INTO goals (user_id, title) VALUES (?, ?)',
            (current_user.id, title)
        )
        goal_id = c.lastrowid
        conn.commit()
        
        return jsonify({
            "message": "Goal added successfully",
            "goal": {
                "id": goal_id,
                "title": title,
                "status": "active"
            }
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/get-goals", methods=["GET"])
@login_required
def get_goals():
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    # Optionally filter by status
    status = request.args.get('status', 'active')
    
    goals = c.execute(
        'SELECT id, title, description, status, target_date FROM goals WHERE user_id = ? AND status = ?', 
        (current_user.id, status)
    ).fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries
    goals_list = [{
        "id": goal[0],
        "title": goal[1],
        "description": goal[2],
        "status": goal[3],
        "target_date": goal[4]
    } for goal in goals]
    
    return jsonify(goals_list), 200

@app.route("/update-goal/<int:goal_id>", methods=["PUT"])
@login_required
def update_goal(goal_id):
    data = request.json
    
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    # Verify goal belongs to current user
    goal = c.execute(
        'SELECT * FROM goals WHERE id = ? AND user_id = ?', 
        (goal_id, current_user.id)
    ).fetchone()
    
    if not goal:
        conn.close()
        return jsonify({"error": "Goal not found"}), 404
    
    # Update fields
    title = data.get('title', goal[2])
    status = data.get('status', goal[4])
    
    try:
        c.execute(
            '''UPDATE goals 
               SET title = ?, status = ?
               WHERE id = ?''',
            (title, status, goal_id)
        )
        conn.commit()
        
        return jsonify({
            "message": "Goal updated successfully",
            "goal": {
                "id": goal_id,
                "title": title,
                "status": status
            }
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/delete-goal/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id):
    conn = sqlite3.connect('instance/database.sqlite')
    c = conn.cursor()
    
    try:
        # First, verify the goal belongs to the current user
        c.execute('DELETE FROM goals WHERE id = ? AND user_id = ?', (goal_id, current_user.id))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({"error": "Goal not found or not authorized"}), 404
        
        conn.commit()
        return jsonify({"message": "Goal deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)