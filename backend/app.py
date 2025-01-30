from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User
from database import init_db
from ai_service import generate_summary, generate_evaluation
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)

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
        
    if User.create(username, password):
        return jsonify({"message": "User created successfully"}), 201
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
        return jsonify({"message": "Logged in successfully"}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

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
        '''SELECT r.answers, r.summary, e.content 
           FROM reports r 
           LEFT JOIN evaluations e ON e.user_id = r.user_id 
           WHERE r.user_id = ? AND r.date = ?''',
        (current_user.id, today)
    ).fetchone()
    
    conn.close()
    
    if report:
        return jsonify({
            "answers": json.loads(report[0]),
            "summary": report[1],
            "evaluation": report[2]
        }), 200
    
    return jsonify({"message": "No report found for today"}), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True)