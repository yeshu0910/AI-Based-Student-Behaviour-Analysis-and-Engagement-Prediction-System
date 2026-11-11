import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user
from database.db import db
from database.models import LabSession, LabTaskAttempt
from modules.auth import student_required
from modules.lab_tasks import LAB_TASKS

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/')
@student_bp.route('/dashboard')
@student_required
def dashboard():
    """
    Student Dashboard: Shows recent sessions, overall progress, and button to start a new lab.
    """
    sessions = LabSession.query.filter_by(student_id=current_user.id).order_by(LabSession.start_time.desc()).all()
    active_session = LabSession.query.filter_by(student_id=current_user.id, status='in_progress').first()
    
    return render_template(
        'student/dashboard.html',
        sessions=sessions,
        active_session=active_session
    )

@student_bp.route('/start', methods=['GET', 'POST'])
@student_required
def start_lab():
    """
    Start Lab Session: Language selection (Python or C) and camera consent.
    Creates LabSession and initializes the 5 task attempts.
    """
    if request.method == 'POST':
        language = request.form.get('language', 'python').lower()
        if language not in ['python', 'c']:
            language = 'python'

        camera_consent = request.form.get('camera_consent') == 'on'

        # Check for any uncompleted session or create new
        session_code = str(uuid.uuid4())
        new_session = LabSession(
            student_id=current_user.id,
            session_code=session_code,
            language=language,
            camera_consent=camera_consent,
            status='in_progress',
            start_time=datetime.now(timezone.utc)
        )
        db.session.add(new_session)
        db.session.flush()

        # Initialize the 5 task attempts for this session
        lang_tasks = LAB_TASKS.get(language, LAB_TASKS['python'])
        for task_num in range(1, 6):
            t_info = lang_tasks.get(task_num, {})
            starter = t_info.get('starter_code', '')
            attempt = LabTaskAttempt(
                session_id=new_session.id,
                task_number=task_num,
                task_title=t_info.get('title', f'Task {task_num}'),
                task_type=t_info.get('type', 'scratch'),
                code_submitted=starter,
                status='pending'
            )
            db.session.add(attempt)

        db.session.commit()
        flash(f'New {language.capitalize()} laboratory session initiated.', 'success')
        return redirect(url_for('lab.workspace', session_code=session_code))

    return render_template('student/start_lab.html')

@student_bp.route('/result/<session_code>')
@student_required
def result(session_code):
    """
    Session completion confirmation page.
    Students see a simple confirmation message acknowledging submission.
    No teacher analytics or AI internal scores are visible to the student.
    """
    session = LabSession.query.filter_by(session_code=session_code, student_id=current_user.id).first_or_404()
    return render_template('student/result.html', session=session)

