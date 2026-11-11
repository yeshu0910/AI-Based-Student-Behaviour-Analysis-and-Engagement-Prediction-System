"""
Activity Tracker Module.
Records programming interactions such as keystrokes, edits, test runs,
navigation, and idle periods during laboratory tasks.
"""
from datetime import datetime, timezone
import json
from database.db import db
from database.models import ProgrammingEvent, LabTaskAttempt

class ActivityTracker:
    @staticmethod
    def record_event(session_id: int, task_number: int, event_type: str, details: dict = None):
        """
        Appends a discrete programming interaction event to the database.
        """
        details_str = json.dumps(details) if details else None
        event = ProgrammingEvent(
            session_id=session_id,
            task_number=task_number,
            event_type=event_type,
            details_json=details_str,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(event)
        
        # If event updates task stats (e.g. typing or edit), update the attempt record
        if event_type in ['edit', 'keystroke']:
            attempt = LabTaskAttempt.query.filter_by(
                session_id=session_id,
                task_number=task_number
            ).first()
            if attempt:
                if event_type == 'edit':
                    attempt.edits_count = (attempt.edits_count or 0) + 1
                elif event_type == 'keystroke':
                    attempt.keystrokes_count = (attempt.keystrokes_count or 0) + 1

        db.session.commit()
        return event

    @staticmethod
    def summarize_activity(session_id: int) -> dict:
        """
        Summarizes student programming activity for the entire laboratory session.
        """
        events = ProgrammingEvent.query.filter_by(session_id=session_id).all()
        attempts = LabTaskAttempt.query.filter_by(session_id=session_id).all()

        total_edits = sum(a.edits_count or 0 for a in attempts)
        total_keystrokes = sum(a.keystrokes_count or 0 for a in attempts)
        total_time_spent = sum(a.time_spent_seconds or 0 for a in attempts)
        
        event_types = {}
        for ev in events:
            event_types[ev.event_type] = event_types.get(ev.event_type, 0) + 1

        idle_events = event_types.get('idle', 0)
        run_events = event_types.get('run_test', 0)
        completed_tasks = sum(1 for a in attempts if a.status == 'completed')

        return {
            'total_events': len(events),
            'total_edits': total_edits,
            'total_keystrokes': total_keystrokes,
            'total_time_spent_seconds': total_time_spent,
            'total_time_spent_minutes': round(total_time_spent / 60.0, 1),
            'idle_count': idle_events,
            'run_test_count': run_events,
            'completed_tasks_count': completed_tasks,
            'event_breakdown': event_types
        }

