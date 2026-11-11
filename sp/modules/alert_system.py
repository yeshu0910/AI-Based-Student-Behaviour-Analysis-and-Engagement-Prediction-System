"""
Alert Question System Module.
Manages timed alert questions displayed during laboratory programming activities.
"""
from datetime import datetime, timezone
from database.db import db
from database.models import AlertQuestion, AlertResponse

class AlertManager:
    @staticmethod
    def get_alert_for_task(language: str, task_number: int):
        """
        Retrieves an alert question tailored to the current task and programming language.
        """
        return AlertQuestion.query.filter_by(
            language=language.lower(),
            task_number=task_number
        ).first()

    @staticmethod
    def record_displayed_alert(session_id: int, alert_id: int):
        """
        Records the moment an alert is triggered and presented to the student.
        """
        existing = AlertResponse.query.filter_by(
            session_id=session_id,
            alert_id=alert_id
        ).first()
        if existing:
            return existing

        response = AlertResponse(
            session_id=session_id,
            alert_id=alert_id,
            displayed_at=datetime.now(timezone.utc),
            status='displayed'
        )
        db.session.add(response)
        db.session.commit()
        return response

    @staticmethod
    def submit_alert_response(session_id: int, alert_id: int, student_answer: str, timeout_seconds: int = 300):
        """
        Validates the student's submission or logs timeout.
        Statuses: 'answered', 'submitted_late', 'timed_out'.
        """
        record = AlertResponse.query.filter_by(
            session_id=session_id,
            alert_id=alert_id
        ).first()

        now = datetime.now(timezone.utc)
        if not record:
            record = AlertResponse(session_id=session_id, alert_id=alert_id, displayed_at=now)
            db.session.add(record)

        alert = AlertQuestion.query.get(alert_id)
        if not alert:
            return None

        # Compute elapsed time
        disp_time = record.displayed_at.replace(tzinfo=timezone.utc) if record.displayed_at.tzinfo is None else record.displayed_at
        elapsed = (now - disp_time).total_seconds()
        record.response_time_seconds = round(elapsed, 1)
        record.responded_at = now
        record.student_answer = student_answer.strip().upper() if student_answer else None

        # Status determination
        if not student_answer or student_answer.upper() == 'TIMEOUT':
            record.status = 'timed_out'
            record.is_correct = False
        elif elapsed > timeout_seconds:
            record.status = 'submitted_late'
            record.is_correct = (record.student_answer == alert.correct_option.strip().upper())
        else:
            record.status = 'answered'
            record.is_correct = (record.student_answer == alert.correct_option.strip().upper())

        db.session.commit()
        return record

    @staticmethod
    def get_session_alert_summary(session_id: int) -> dict:
        """
        Returns analytics on alerts answered, timed out, and accuracy for the session.
        """
        responses = AlertResponse.query.filter_by(session_id=session_id).all()
        total_triggered = len(responses)
        answered = sum(1 for r in responses if r.status in ['answered', 'submitted_late'])
        timed_out = sum(1 for r in responses if r.status == 'timed_out')
        correct = sum(1 for r in responses if r.is_correct)
        avg_time = round(sum(r.response_time_seconds for r in responses if r.response_time_seconds) / max(1, answered), 1)

        return {
            'total_alerts': total_triggered,
            'answered_count': answered,
            'timed_out_count': timed_out,
            'correct_count': correct,
            'accuracy_pct': round((correct / max(1, answered)) * 100.0, 1) if answered > 0 else 0.0,
            'avg_response_time_sec': avg_time,
            'responses': responses
        }

