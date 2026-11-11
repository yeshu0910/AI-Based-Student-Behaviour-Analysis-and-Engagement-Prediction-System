from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database.db import db
from database.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access restricted to students.', 'danger')
            return redirect(url_for('teacher.dashboard' if current_user.is_teacher else 'auth.student_login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('Access restricted to teachers and administrators.', 'danger')
            return redirect(url_for('student.dashboard' if current_user.is_student else 'auth.teacher_login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Dedicated Student Login Portal"""
    if current_user.is_authenticated:
        if current_user.is_student:
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            if user.role != 'student':
                flash('This account is registered as Faculty/Teacher. Please use the Teacher Login portal.', 'warning')
                return redirect(url_for('auth.teacher_login'))

            login_user(user, remember=True)
            flash(f'Welcome to your Virtual Lab, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page or url_for('student.dashboard'))
        else:
            flash('Invalid student username or password. Please try again.', 'danger')

    return render_template('auth/student_login.html')

@auth_bp.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    """Dedicated Teacher / Faculty Login Portal"""
    if current_user.is_authenticated:
        if current_user.is_teacher:
            return redirect(url_for('teacher.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            if user.role != 'teacher':
                flash('This account is registered as Student. Please use the Student Login portal.', 'warning')
                return redirect(url_for('auth.student_login'))

            login_user(user, remember=True)
            flash(f'Welcome back, Professor {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page or url_for('teacher.dashboard'))
        else:
            flash('Invalid faculty username or password. Please try again.', 'danger')

    return render_template('auth/teacher_login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """General Login redirecting by role or showing role selector"""
    role = request.args.get('role')
    if role == 'teacher':
        return redirect(url_for('auth.teacher_login'))
    elif role == 'student':
        return redirect(url_for('auth.student_login'))

    if current_user.is_authenticated:
        return redirect(url_for('teacher.dashboard' if current_user.is_teacher else 'student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('teacher.dashboard' if user.is_teacher else 'student.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('teacher.dashboard' if current_user.is_teacher else 'student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student').strip().lower()
        if role not in ['student', 'teacher']:
            role = 'student'

        if not username or not email or not password or not full_name:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'warning')
            return render_template('auth/register.html')

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You may now sign in.', 'success')
        return redirect(url_for('auth.student_login' if role == 'student' else 'auth.teacher_login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))
