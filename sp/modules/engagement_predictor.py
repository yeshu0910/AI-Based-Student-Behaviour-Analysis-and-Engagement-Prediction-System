"""
Engagement Prediction Engine.
Fuses multimodal indicators (Visual, Programming, Alert, Assessment)
to determine engagement categories ('Low Engagement', 'Moderate Engagement', 'High Engagement').
Supports Scikit-Learn trained models with a calibrated rule-based fallback.
"""
import os
import joblib
import json
from datetime import datetime, timezone
from database.db import db
from database.models import LabSession, EngagementPrediction
from modules.feature_extraction import FeatureExtractor
from config import Config

class EngagementPredictor:
    _model = None
    _model_metadata = None

    @classmethod
    def load_model(cls):
        """
        Loads pre-trained Random Forest / Ensemble model if available on disk.
        """
        if cls._model is not None:
            return cls._model

        model_path = os.path.join(Config.TRAINED_MODELS_DIR, 'engagement_model.pkl')
        meta_path = os.path.join(Config.TRAINED_MODELS_DIR, 'model_metadata.json')

        if os.path.exists(model_path):
            try:
                cls._model = joblib.load(model_path)
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        cls._model_metadata = json.load(f)
                return cls._model
            except Exception as e:
                print(f"[Warning] Could not load trained ML model: {e}. Using calibrated multimodal fusion.")
                cls._model = None
        return None

    @classmethod
    def predict_session_engagement(cls, session: LabSession) -> EngagementPrediction:
        """
        Evaluates a session and returns or stores an EngagementPrediction record.
        """
        features = FeatureExtractor.extract_session_features(session)
        indicators = []
        warnings = []

        # 1. Visual Score (0-100)
        # Important: If visual data is missing/declined, do NOT penalize as low engagement!
        if features['has_visual_data']:
            editor_attn = features['editor_attention_pct'] or 50.0
            face_vis = features['face_visibility_pct'] or 70.0
            outside_attn = features['outside_attention_pct'] or 10.0
            
            # Focused attention score
            v_score = (editor_attn * 0.6) + (face_vis * 0.3) - (outside_attn * 0.2)
            visual_score = max(10.0, min(100.0, round(v_score, 1)))
            indicators.append(f"Visual gaze on code/instructions: {editor_attn}% of active time.")
        else:
            visual_score = None
            if not features['camera_consent']:
                warnings.append("Camera permission was declined by the student; visual metrics excluded from evaluation.")
            else:
                warnings.append("Camera feed was unavailable or insufficient observations recorded.")

        # 2. Programming Activity Score (0-100)
        tasks_completed = features['tasks_completed']
        keystrokes = features['total_keystrokes']
        edits = features['total_edits']
        runs = features['run_events_count']
        
        # Benchmarks: 5 tasks completed = 50 pts; active typing & edits = up to 35 pts; test runs = 15 pts
        prog_score = (tasks_completed / 5.0) * 50.0
        prog_score += min(35.0, (keystrokes / 150.0) * 20.0 + (edits / 30.0) * 15.0)
        prog_score += min(15.0, runs * 5.0)
        programming_score = max(15.0, min(100.0, round(prog_score, 1)))
        
        indicators.append(f"Completed {tasks_completed}/5 programming tasks with {edits} edits and {keystrokes} keystrokes.")

        # 3. Alert Response Score (0-100)
        total_alerts = features['total_alerts']
        if total_alerts > 0:
            answered_ratio = features['alerts_answered'] / total_alerts
            correct_ratio = features['alerts_correct'] / max(1, features['alerts_answered'])
            a_score = (answered_ratio * 60.0) + (correct_ratio * 40.0)
            alert_score = max(10.0, min(100.0, round(a_score, 1)))
            indicators.append(f"Answered {features['alerts_answered']}/{total_alerts} timed alert checks with {features['alerts_correct']} correct.")
        else:
            alert_score = None
            warnings.append("No timed alert checks were triggered or answered during this session.")

        # 4. Assessment Score (0-100)
        if features['assessment_completed']:
            assessment_score = float(features['assessment_pct'])
            indicators.append(f"Final assessment score: {features['assessment_score']}/10 ({assessment_score}%).")
        else:
            assessment_score = 0.0
            warnings.append("Final 10-question assessment has not yet been submitted.")

        # Multimodal Fusion: Dynamic weight adjustment based on available modalities
        weights = {}
        if visual_score is not None:
            weights['visual'] = 0.25
        weights['programming'] = 0.35 if visual_score is not None else 0.45
        if alert_score is not None:
            weights['alert'] = 0.15
        else:
            weights['programming'] += 0.05
        weights['assessment'] = 0.25 if visual_score is not None else 0.35

        # Normalize weights
        total_weight = sum(weights.values())
        norm_weights = {k: v / total_weight for k, v in weights.items()}

        composite_score = (
            (visual_score or 0) * norm_weights.get('visual', 0) +
            programming_score * norm_weights.get('programming', 0) +
            (alert_score or 0) * norm_weights.get('alert', 0) +
            assessment_score * norm_weights.get('assessment', 0)
        )
        composite_score = round(max(0.0, min(100.0, composite_score)), 1)

        # Classify engagement category
        if composite_score >= 70.0:
            category = 'High Engagement'
        elif composite_score >= 42.0:
            category = 'Moderate Engagement'
        else:
            category = 'Low Engagement'

        # Estimate confidence
        active_modalities = sum([visual_score is not None, programming_score > 0, alert_score is not None, features['assessment_completed']])
        confidence = round(0.55 + (active_modalities * 0.1), 2)

        summary_payload = {
            'weights_applied': norm_weights,
            'indicators': indicators,
            'warnings': warnings,
            'features_snapshot': features,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Store or update database record
        prediction = EngagementPrediction.query.filter_by(session_id=session.id).first()
        if not prediction:
            prediction = EngagementPrediction(
                session_id=session.id,
                student_id=session.student_id
            )
            db.session.add(prediction)

        prediction.visual_score = visual_score or 0.0
        prediction.programming_score = programming_score
        prediction.alert_score = alert_score or 0.0
        prediction.assessment_score = assessment_score
        prediction.overall_engagement_score = composite_score
        prediction.predicted_category = category
        prediction.confidence = min(0.98, confidence)
        prediction.feature_summary_json = json.dumps(summary_payload)

        db.session.commit()
        return prediction

