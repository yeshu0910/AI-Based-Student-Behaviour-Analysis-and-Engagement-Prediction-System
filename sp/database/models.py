from datetime import datetime, timezone
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student' or 'teacher'
    full_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sessions = db.relationship('LabSession', backref='student', lazy=True, foreign_keys='LabSession.student_id')
    assessment_attempts = db.relationship('AssessmentAttempt', backref='student', lazy=True)
    engagement_predictions = db.relationship('EngagementPrediction', backref='student', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class LabSession(db.Model):
    __tablename__ = 'lab_sessions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_code = db.Column(db.String(36), unique=True, nullable=False, index=True)
    language = db.Column(db.String(20), nullable=False, default='python') # 'python' or 'c'
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), nullable=False, default='in_progress') # 'in_progress', 'completed', 'abandoned'
    camera_consent = db.Column(db.Boolean, default=False)
    
    # Relationships
    task_attempts = db.relationship('LabTaskAttempt', backref='session', lazy=True, cascade='all, delete-orphan')
    programming_events = db.relationship('ProgrammingEvent', backref='session', lazy=True, cascade='all, delete-orphan')
    gaze_observations = db.relationship('GazeObservation', backref='session', lazy=True, cascade='all, delete-orphan')
    alert_responses = db.relationship('AlertResponse', backref='session', lazy=True, cascade='all, delete-orphan')
    assessment_attempt = db.relationship('AssessmentAttempt', backref='session', uselist=False, cascade='all, delete-orphan')
    prediction = db.relationship('EngagementPrediction', backref='session', uselist=False, cascade='all, delete-orphan')

    def get_duration_minutes(self):
        if self.end_time and self.start_time:
            return round((self.end_time - self.start_time).total_seconds() / 60.0, 1)
        elif self.start_time:
            return round((datetime.now(timezone.utc) - self.start_time.replace(tzinfo=timezone.utc)).total_seconds() / 60.0, 1)
        return 0.0


class LabTaskAttempt(db.Model):
    __tablename__ = 'lab_task_attempts'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_sessions.id'), nullable=False, index=True)
    task_number = db.Column(db.Integer, nullable=False) # 1 to 5
    task_title = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False) # scratch, jumble, fill, debug, predict
    code_submitted = db.Column(db.Text, nullable=True)
    execution_output = db.Column(db.Text, nullable=True)
    is_passed = db.Column(db.Boolean, default=False)
    edits_count = db.Column(db.Integer, default=0)
    keystrokes_count = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    submit_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), default='pending') # 'pending', 'completed'


class ProgrammingEvent(db.Model):
    __tablename__ = 'programming_events'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_sessions.id'), nullable=False, index=True)
    task_number = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # edit, keystroke, idle, run_test, copy_paste, tab_switch
    details_json = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class GazeObservation(db.Model):
    __tablename__ = 'gaze_observations'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_sessions.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    face_detected = db.Column(db.Boolean, default=True)
    head_pose_pitch = db.Column(db.Float, default=0.0)
    head_pose_yaw = db.Column(db.Float, default=0.0)
    head_pose_roll = db.Column(db.Float, default=0.0)
    gaze_x = db.Column(db.Float, default=0.5) # Normalized 0.0 - 1.0
    gaze_y = db.Column(db.Float, default=0.5) # Normalized 0.0 - 1.0
    screen_area = db.Column(db.String(50), default='unknown') # 'code_editor', 'instructions', 'console', 'outside', 'unknown'
    fixation_duration = db.Column(db.Float, default=0.0) # Seconds


class AlertQuestion(db.Model):
    __tablename__ = 'alert_questions'

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20), nullable=False) # python or c
    task_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(10), nullable=False) # A, B, C, D


class AlertResponse(db.Model):
    __tablename__ = 'alert_responses'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_sessions.id'), nullable=False, index=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alert_questions.id'), nullable=False)
    displayed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    responded_at = db.Column(db.DateTime, nullable=True)
    student_answer = db.Column(db.String(10), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    response_time_seconds = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='displayed') # answered, submitted_late, timed_out

    alert_question = db.relationship('AlertQuestion', backref='responses')


class AssessmentQuestion(db.Model):
    __tablename__ = 'assessment_questions'

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20), nullable=False) # python or c
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(10), nullable=False)
    topic = db.Column(db.String(100), default='General')


class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempts'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_sessions.id'), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=10)
    answers_json = db.Column(db.Text, nullable=True) # JSON dictionary of question_id -> chosen_option
    start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    submit_time = db.Column(db.DateTime, nullable=True)
    completion_time_seconds = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='in_progress') # 'in_progress', 'completed'

    def get_answers_dict(self):
        if self.answers_json:
            try:
                return json.loads(self.answers_json)
            except Exception:
                return {}
        return {}


class EngagementPrediction(db.Model):
    __tablename__ = 'engagement_predictions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_sessions.id'), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visual_score = db.Column(db.Float, default=0.0) # 0 to 100
    programming_score = db.Column(db.Float, default=0.0) # 0 to 100
    alert_score = db.Column(db.Float, default=0.0) # 0 to 100
    assessment_score = db.Column(db.Float, default=0.0) # 0 to 100
    overall_engagement_score = db.Column(db.Float, default=0.0) # 0 to 100
    predicted_category = db.Column(db.String(30), default='Moderate Engagement') # Low Engagement, Moderate Engagement, High Engagement
    confidence = db.Column(db.Float, default=0.85)
    feature_summary_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_summary_dict(self):
        if self.feature_summary_json:
            try:
                return json.loads(self.feature_summary_json)
            except Exception:
                return {}
        return {}

