"""
Feature Extraction and Multimodal Fusion Pipeline.
Aggregates Visual, Programming, Alert, and Assessment data points
into normalized numerical feature vectors for ML engagement inference.
"""
from database.models import LabSession, GazeObservation, LabTaskAttempt, ProgrammingEvent, AlertResponse, AssessmentAttempt
from modules.gaze_estimation import ScreenAreaMapper

class FeatureExtractor:
    @staticmethod
    def extract_session_features(session: LabSession) -> dict:
        """
        Extracts comprehensive multimodal feature dictionary for a given lab session.
        Handles missing modalities gracefully without false negative penalties.
        """
        # 1. Visual Features
        gaze_obs = GazeObservation.query.filter_by(session_id=session.id).all()
        visual_summary = ScreenAreaMapper.calculate_fixation_and_attention(gaze_obs)
        
        has_camera_data = len(gaze_obs) > 5 and visual_summary['face_visibility_pct'] > 10.0
        face_visibility_pct = visual_summary['face_visibility_pct'] if has_camera_data else None
        editor_attention_pct = visual_summary['editor_pct'] if has_camera_data else None
        outside_attention_pct = visual_summary['outside_pct'] if has_camera_data else None
        avg_fixation = visual_summary['avg_fixation_seconds'] if has_camera_data else None

        # 2. Programming Activity Features
        attempts = LabTaskAttempt.query.filter_by(session_id=session.id).all()
        events = ProgrammingEvent.query.filter_by(session_id=session.id).all()

        total_edits = sum(a.edits_count or 0 for a in attempts)
        total_keystrokes = sum(a.keystrokes_count or 0 for a in attempts)
        total_task_time = sum(a.time_spent_seconds or 0 for a in attempts)
        tasks_completed = sum(1 for a in attempts if a.status == 'completed')
        tasks_passed = sum(1 for a in attempts if a.is_passed)
        idle_events = sum(1 for e in events if e.event_type == 'idle')
        run_events = sum(1 for e in events if e.event_type == 'run_test')

        # 3. Alert Question Features
        alert_responses = AlertResponse.query.filter_by(session_id=session.id).all()
        total_alerts = len(alert_responses)
        alerts_answered = sum(1 for r in alert_responses if r.status in ['answered', 'submitted_late'])
        alerts_timed_out = sum(1 for r in alert_responses if r.status == 'timed_out')
        alerts_correct = sum(1 for r in alert_responses if r.is_correct)
        avg_alert_resp_time = (
            sum(r.response_time_seconds for r in alert_responses if r.response_time_seconds) / max(1, alerts_answered)
            if alerts_answered > 0 else 0.0
        )

        # 4. Assessment Features
        assessment = AssessmentAttempt.query.filter_by(session_id=session.id).first()
        assessment_score = assessment.total_score if assessment else 0
        assessment_max = assessment.max_score if assessment else 10
        assessment_pct = round((assessment_score / max(1, assessment_max)) * 100.0, 1) if assessment else 0.0
        assessment_completed = assessment is not None and assessment.status == 'completed'

        return {
            'session_id': session.id,
            'language': session.language,
            'duration_minutes': session.get_duration_minutes(),
            
            # Modality availability flags
            'has_visual_data': has_camera_data,
            'camera_consent': session.camera_consent,
            
            # Visual indicators
            'face_visibility_pct': face_visibility_pct,
            'editor_attention_pct': editor_attention_pct,
            'outside_attention_pct': outside_attention_pct,
            'avg_fixation_seconds': avg_fixation,
            'visual_quality_warning': visual_summary.get('data_quality_warning'),
            
            # Programming indicators
            'total_edits': total_edits,
            'total_keystrokes': total_keystrokes,
            'tasks_completed': tasks_completed,
            'tasks_passed': tasks_passed,
            'total_task_time_seconds': total_task_time,
            'idle_events_count': idle_events,
            'run_events_count': run_events,
            
            # Alert indicators
            'total_alerts': total_alerts,
            'alerts_answered': alerts_answered,
            'alerts_timed_out': alerts_timed_out,
            'alerts_correct': alerts_correct,
            'avg_alert_resp_time': round(avg_alert_resp_time, 1),
            
            # Assessment indicators
            'assessment_score': assessment_score,
            'assessment_pct': assessment_pct,
            'assessment_completed': assessment_completed
        }

