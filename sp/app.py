"""
AI-Based Student Behaviour Analysis and Engagement Prediction System
Main Flask Application Entry Point
"""
import os
from flask import Flask, redirect, url_for, render_template
from flask_login import current_user
from config import Config
from database.db import db, login_manager
from database.models import User
from modules.auth import auth_bp
from modules.student_routes import student_bp
from modules.lab_routes import lab_bp
from modules.teacher_routes import teacher_bp
from modules.seeder import seed_database
from modules.engagement_predictor import EngagementPredictor

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(teacher_bp)

    # Main Home Landing Route (Portal Selection)
    @app.route('/', endpoint='home')
    @app.route('/home', endpoint='home_page')
    def home():
        if current_user.is_authenticated:
            if current_user.is_teacher:
                return redirect(url_for('teacher.dashboard'))
            return redirect(url_for('student.dashboard'))
        return render_template('home.html')

    # Initialize Database & Seed Default Records
    with app.app_context():
        # Ensure database directory exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        db.create_all()
        seed_database()
        
        # Load trained ML model in predictor
        EngagementPredictor.load_model()

    return app

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 65)
    print(" AI-Based Student Behaviour Analysis & Engagement Prediction System")
    print(" Server running on: http://127.0.0.1:5000")
    print(" Student Login Portal: http://127.0.0.1:5000/auth/student/login")
    print(" Teacher Login Portal: http://127.0.0.1:5000/auth/teacher/login")
    print("=" * 65 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
