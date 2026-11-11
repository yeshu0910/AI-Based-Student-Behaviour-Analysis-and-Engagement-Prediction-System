from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user
from database.db import db
from database.models import LabSession, LabTaskAttempt, GazeObservation
from modules.auth import student_required
from modules.lab_tasks import LAB_TASKS
from modules.code_executor import CodeExecutor
from modules.activity_tracker import ActivityTracker
from modules.alert_system import AlertManager
from modules.assessment import AssessmentManager
from modules.gaze_estimation import ScreenAreaMapper
from modules.engagement_predictor import EngagementPredictor

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')

def get_authorized_session(session_code):
    session = LabSession.query.filter_by(session_code=session_code).first_or_404()
    if session.student_id != current_user.id and not current_user.is_teacher:
        abort(403)
    return session

@lab_bp.route('/<session_code>')
@student_required
def workspace(session_code):
    session = get_authorized_session(session_code)
    
    # If session is already completed, redirect to completion notice
    if session.status == 'completed':
        return redirect(url_for('student.result', session_code=session_code))

    task_number = request.args.get('task', 1, type=int)
    if task_number < 1 or task_number > 5:
        task_number = 1

    attempts = LabTaskAttempt.query.filter_by(session_id=session.id).order_by(LabTaskAttempt.task_number.asc()).all()
    current_attempt = next((a for a in attempts if a.task_number == task_number), None)
    
    # Check if all 5 are already completed
    all_completed = len(attempts) == 5 and all(a.status == 'completed' for a in attempts)
    if all_completed:
        return redirect(url_for('lab.tasks_completed', session_code=session_code))

    lang_tasks = LAB_TASKS.get(session.language, LAB_TASKS['python'])
    task_spec = lang_tasks.get(task_number, {})

    return render_template(
        'student/lab.html',
        session=session,
        attempts=attempts,
        current_attempt=current_attempt,
        current_task_num=task_number,
        task_spec=task_spec
    )

@lab_bp.route('/<session_code>/run', methods=['POST'])
@student_required
def run_code(session_code):
    session = get_authorized_session(session_code)
    data = request.get_json() or {}
    code = data.get('code', '')
    test_input = data.get('input', '')
    task_number = data.get('task_number', 1)

    # Record run event
    ActivityTracker.record_event(session.id, task_number, 'run_test', {'code_length': len(code)})

    if session.language == 'c':
        result = CodeExecutor.execute_c(code, test_input)
    else:
        result = CodeExecutor.execute_python(code, test_input)

    return jsonify(result)

@lab_bp.route('/<session_code>/submit-task', methods=['POST'])
@student_required
def submit_task(session_code):
    session = get_authorized_session(session_code)
    data = request.get_json() or {}
    task_number = data.get('task_number', 1)
    code = data.get('code', '')
    time_spent = data.get('time_spent', 0)
    edits = data.get('edits', 0)
    keystrokes = data.get('keystrokes', 0)

    attempt = LabTaskAttempt.query.filter_by(
        session_id=session.id,
        task_number=task_number
    ).first_or_404()

    attempt.code_submitted = code
    attempt.time_spent_seconds = (attempt.time_spent_seconds or 0) + int(time_spent)
    attempt.edits_count = (attempt.edits_count or 0) + int(edits)
    attempt.keystrokes_count = (attempt.keystrokes_count or 0) + int(keystrokes)
    attempt.submit_time = datetime.now(timezone.utc)
    attempt.status = 'completed'

    # Verify output or code correctness if possible
    lang_tasks = LAB_TASKS.get(session.language, LAB_TASKS['python'])
    spec = lang_tasks.get(task_number, {})
    expected = spec.get('expected_output', '').strip()
    
    if spec.get('type') == 'predict':
        attempt.is_passed = (code.strip() == spec.get('correct_option', '').strip())
    else:
        # Run test check
        if session.language == 'c':
            exec_res = CodeExecutor.execute_c(code, spec.get('sample_input', ''))
        else:
            exec_res = CodeExecutor.execute_python(code, spec.get('sample_input', ''))
        
        attempt.execution_output = exec_res.get('output', '')
        attempt.is_passed = expected in exec_res.get('output', '') if expected else exec_res.get('success', False)

    db.session.commit()

    # Check if all 5 tasks are now complete
    all_attempts = LabTaskAttempt.query.filter_by(session_id=session.id).all()
    all_done = len(all_attempts) == 5 and all(a.status == 'completed' for a in all_attempts)

    next_task = task_number + 1 if task_number < 5 else None

    return jsonify({
        'success': True,
        'task_number': task_number,
        'all_done': all_done,
        'next_task': next_task,
        'is_passed': attempt.is_passed,
        'redirect_url': url_for('lab.tasks_completed', session_code=session_code) if all_done else None
    })

@lab_bp.route('/<session_code>/tasks-completed')
@student_required
def tasks_completed(session_code):
    session = get_authorized_session(session_code)
    attempts = LabTaskAttempt.query.filter_by(session_id=session.id).order_by(LabTaskAttempt.task_number.asc()).all()
    return render_template('student/tasks_completed.html', session=session, attempts=attempts)

@lab_bp.route('/<session_code>/telemetry/event', methods=['POST'])
@student_required
def telemetry_event(session_code):
    session = get_authorized_session(session_code)
    data = request.get_json() or {}
    event_type = data.get('event_type', 'typing')
    task_number = data.get('task_number', 1)
    details = data.get('details', {})

    ActivityTracker.record_event(session.id, task_number, event_type, details)
    return jsonify({'status': 'ok'})

@lab_bp.route('/<session_code>/telemetry/gaze', methods=['POST'])
@student_required
def telemetry_gaze(session_code):
    session = get_authorized_session(session_code)
    data = request.get_json() or {}
    
    face_detected = data.get('face_detected', False)
    gaze_x = data.get('gaze_x')
    gaze_y = data.get('gaze_y')
    head_pose = data.get('head_pose', {})
    fixation = data.get('fixation_duration', 1.0)

    area = ScreenAreaMapper.map_coordinates_to_area(gaze_x, gaze_y, face_detected)

    obs = GazeObservation(
        session_id=session.id,
        timestamp=datetime.now(timezone.utc),
        face_detected=bool(face_detected),
        head_pose_pitch=float(head_pose.get('pitch', 0.0)),
        head_pose_yaw=float(head_pose.get('yaw', 0.0)),
        head_pose_roll=float(head_pose.get('roll', 0.0)),
        gaze_x=float(gaze_x) if gaze_x is not None else 0.5,
        gaze_y=float(gaze_y) if gaze_y is not None else 0.5,
        screen_area=area,
        fixation_duration=float(fixation)
    )
    db.session.add(obs)
    db.session.commit()
    return jsonify({'status': 'ok', 'area': area})

@lab_bp.route('/<session_code>/alert/get')
@student_required
def get_alert(session_code):
    session = get_authorized_session(session_code)
    task_number = request.args.get('task', 1, type=int)

    alert = AlertManager.get_alert_for_task(session.language, task_number)
    if not alert:
        return jsonify({'has_alert': False})

    # Record that the alert was triggered/displayed
    record = AlertManager.record_displayed_alert(session.id, alert.id)
    if record.status in ['answered', 'timed_out', 'submitted_late']:
        return jsonify({'has_alert': False, 'already_completed': True})

    return jsonify({
        'has_alert': True,
        'alert_id': alert.id,
        'task_number': alert.task_number,
        'question': alert.question_text,
        'options': {
            'A': alert.option_a,
            'B': alert.option_b,
            'C': alert.option_c,
            'D': alert.option_d
        },
        'timeout_seconds': 300
    })

@lab_bp.route('/<session_code>/alert/respond', methods=['POST'])
@student_required
def respond_alert(session_code):
    session = get_authorized_session(session_code)
    data = request.get_json() or {}
    alert_id = data.get('alert_id')
    answer = data.get('answer', '')
    
    record = AlertManager.submit_alert_response(session.id, int(alert_id), answer)
    return jsonify({
        'status': record.status if record else 'error',
        'is_correct': record.is_correct if record else False
    })

@lab_bp.route('/<session_code>/assessment', methods=['GET'])
@student_required
def assessment(session_code):
    session = get_authorized_session(session_code)
    questions = AssessmentManager.get_questions_for_session(session.language, limit=10)
    existing_attempt = session.assessment_attempt

    return render_template(
        'student/assessment.html',
        session=session,
        questions=questions,
        existing_attempt=existing_attempt
    )

@lab_bp.route('/<session_code>/assessment/submit', methods=['POST'])
@student_required
def submit_assessment(session_code):
    session = get_authorized_session(session_code)
    answers = {}
    for key, value in request.form.items():
        if key.startswith('q_'):
            q_id = key.split('_')[1]
            answers[q_id] = value

    # Process assessment grading
    AssessmentManager.submit_assessment(session.id, current_user.id, answers)

    # Finalize laboratory session
    session.status = 'completed'
    session.end_time = datetime.now(timezone.utc)
    db.session.commit()

    # Trigger ML engagement prediction and feature fusion
    EngagementPredictor.predict_session_engagement(session)

    flash('Assessment submitted successfully. Your session is now complete!', 'success')
    return redirect(url_for('student.result', session_code=session_code))

