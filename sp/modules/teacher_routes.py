import io
import csv
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, abort
from database.db import db
from database.models import User, LabSession, LabTaskAttempt, GazeObservation, AlertResponse, AssessmentAttempt, EngagementPrediction
from modules.auth import teacher_required
from modules.gaze_estimation import ScreenAreaMapper
from modules.activity_tracker import ActivityTracker
from modules.alert_system import AlertManager
from modules.assessment import AssessmentManager
from modules.engagement_predictor import EngagementPredictor

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/')
@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    """
    Teacher Portal Dashboard: High-level analytics, key performance indicators,
    and list of all student lab sessions.
    """
    students = User.query.filter_by(role='student').order_by(User.full_name.asc()).all()
    sessions = LabSession.query.order_by(LabSession.start_time.desc()).all()

    total_students = len(students)
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.status == 'completed')
    active_sessions = sum(1 for s in sessions if s.status == 'in_progress')
    
    predictions = EngagementPrediction.query.all()
    category_counts = {
        'High Engagement': 0,
        'Moderate Engagement': 0,
        'Low Engagement': 0
    }
    for p in predictions:
        cat = p.predicted_category
        if cat in category_counts:
            category_counts[cat] += 1

    return render_template(
        'teacher/dashboard.html',
        total_students=total_students,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        active_sessions=active_sessions,
        category_counts=category_counts,
        sessions=sessions,
        students=students
    )

@teacher_bp.route('/student/<int:student_id>')
@teacher_required
def student_detail(student_id):
    """
    Detailed profile and historical laboratory performance for an individual student.
    """
    student = User.query.filter_by(id=student_id, role='student').first_or_404()
    sessions = LabSession.query.filter_by(student_id=student.id).order_by(LabSession.start_time.desc()).all()
    
    return render_template(
        'teacher/student_detail.html',
        student=student,
        sessions=sessions
    )

@teacher_bp.route('/session/<int:session_id>')
@teacher_required
def session_detail(session_id):
    """
    Deep-dive Session Analytics:
    - Task-by-task code submissions and test metrics
    - Eye-gaze coordinate plots and screen area distribution
    - Timed alert question responses
    - Final assessment answers and score breakdown
    - AI multimodal engagement prediction and confidence
    """
    session = LabSession.query.get_or_404(session_id)
    
    # Refresh or create engagement prediction if not present or session completed
    prediction = session.prediction
    if not prediction or session.status == 'completed':
        prediction = EngagementPredictor.predict_session_engagement(session)

    # 1. Tasks
    task_attempts = LabTaskAttempt.query.filter_by(session_id=session.id).order_by(LabTaskAttempt.task_number.asc()).all()
    
    # 2. Activity Summary
    activity_summary = ActivityTracker.summarize_activity(session.id)
    
    # 3. Gaze & Visual Tracking
    gaze_obs = GazeObservation.query.filter_by(session_id=session.id).order_by(GazeObservation.timestamp.asc()).all()
    gaze_analytics = ScreenAreaMapper.calculate_fixation_and_attention(gaze_obs)
    
    # Sample down gaze coordinates for clean chart plotting (max 100 points)
    step = max(1, len(gaze_obs) // 100) if len(gaze_obs) > 100 else 1
    sampled_gaze = [
        {
            'x': round(o.gaze_x, 3),
            'y': round(o.gaze_y, 3),
            'area': o.screen_area,
            'face_detected': o.face_detected,
            'time': o.timestamp.strftime('%H:%M:%S')
        }
        for o in gaze_obs[::step]
    ]

    # 4. Alert Responses
    alert_summary = AlertManager.get_session_alert_summary(session.id)

    # 5. Assessment Attempt
    assessment_details = AssessmentManager.get_attempt_details(session.id)

    return render_template(
        'teacher/session_detail.html',
        session=session,
        prediction=prediction,
        task_attempts=task_attempts,
        activity_summary=activity_summary,
        gaze_analytics=gaze_analytics,
        sampled_gaze=sampled_gaze,
        alert_summary=alert_summary,
        assessment_details=assessment_details
    )

@teacher_bp.route('/reports')
@teacher_required
def reports():
    """
    Aggregated Analytics & Reports View.
    """
    sessions = LabSession.query.order_by(LabSession.start_time.desc()).all()
    predictions = EngagementPrediction.query.all()
    
    high_count = sum(1 for p in predictions if p.predicted_category == 'High Engagement')
    mod_count = sum(1 for p in predictions if p.predicted_category == 'Moderate Engagement')
    low_count = sum(1 for p in predictions if p.predicted_category == 'Low Engagement')

    return render_template(
        'teacher/reports.html',
        sessions=sessions,
        high_count=high_count,
        mod_count=mod_count,
        low_count=low_count
    )

@teacher_bp.route('/export/csv')
@teacher_required
def export_csv():
    """
    Exports comprehensive session metrics, student performance, and AI predictions to CSV.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Session ID', 'Session Code', 'Student ID', 'Student Name', 'Student Email',
        'Language', 'Status', 'Start Time', 'Duration (mins)',
        'Camera Consent', 'Face Visibility %', 'Editor Attention %',
        'Total Edits', 'Total Keystrokes', 'Tasks Completed',
        'Alerts Answered', 'Alerts Correct', 'Assessment Score',
        'Overall Engagement Score', 'Predicted Category', 'Confidence'
    ])

    sessions = LabSession.query.order_by(LabSession.id.asc()).all()
    for s in sessions:
        student = s.student
        p = s.prediction
        gaze_obs = GazeObservation.query.filter_by(session_id=s.id).all()
        g_summary = ScreenAreaMapper.calculate_fixation_and_attention(gaze_obs)
        act = ActivityTracker.summarize_activity(s.id)
        alrt = AlertManager.get_session_alert_summary(s.id)
        assm = s.assessment_attempt

        writer.writerow([
            s.id, s.session_code, student.id if student else '',
            student.full_name if student else 'Unknown',
            student.email if student else '',
            s.language, s.status, s.start_time.strftime('%Y-%m-%d %H:%M:%S') if s.start_time else '',
            s.get_duration_minutes(),
            'Yes' if s.camera_consent else 'No',
            g_summary['face_visibility_pct'],
            g_summary['editor_pct'],
            act['total_edits'],
            act['total_keystrokes'],
            act['completed_tasks_count'],
            alrt['answered_count'],
            alrt['correct_count'],
            f"{assm.total_score}/{assm.max_score}" if assm else 'N/A',
            p.overall_engagement_score if p else 'N/A',
            p.predicted_category if p else 'N/A',
            p.confidence if p else 'N/A'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=lab_engagement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

