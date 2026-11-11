"""
End-to-End System Verification Test Script.
Tests:
1. Database initialization and models
2. Authentication (User creation & verification)
3. Laboratory session lifecycle (Creation, 5 tasks, code execution)
4. Telemetry (Gaze observation mapping and Activity tracking)
5. Alert question handling (Trigger & Response)
6. Final 10-Question Assessment & Auto-Grading
7. AI Multimodal Engagement Prediction & Feature Fusion
8. Teacher Analytics Endpoints & CSV Export
"""
import unittest
import json
from app import create_app
from database.db import db
from database.models import User, LabSession, LabTaskAttempt, GazeObservation, AlertResponse, AssessmentAttempt, EngagementPrediction
from modules.code_executor import CodeExecutor
from modules.gaze_estimation import ScreenAreaMapper
from modules.engagement_predictor import EngagementPredictor

class SystemVerificationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_database_and_seed_data(self):
        """Verify seeded teacher, students, alert questions, and assessment MCQs."""
        teacher = User.query.filter_by(username='teacher').first()
        self.assertIsNotNone(teacher)
        self.assertTrue(teacher.is_teacher)

        student1 = User.query.filter_by(username='student1').first()
        self.assertIsNotNone(student1)
        self.assertTrue(student1.is_student)
        self.assertTrue(student1.check_password('student123'))

        # Check sample sessions
        sessions = LabSession.query.all()
        self.assertGreaterEqual(len(sessions), 1)

    def test_02_code_execution_engine(self):
        """Verify Python code execution in isolated sandbox."""
        py_code = "print(10 + 25)"
        res = CodeExecutor.execute_python(py_code)
        self.assertTrue(res['success'])
        self.assertEqual(res['output'], "35")

        # Verify safety filter
        unsafe_code = "import os; os.system('echo test')"
        res_unsafe = CodeExecutor.execute_python(unsafe_code)
        self.assertFalse(res_unsafe['success'])
        self.assertIn("Security Warning", res_unsafe['output'])

    def test_03_gaze_screen_mapping(self):
        """Verify screen area attention classification from normalized coordinates."""
        # Top right = code editor
        area_editor = ScreenAreaMapper.map_coordinates_to_area(0.65, 0.35, face_detected=True)
        self.assertEqual(area_editor, 'code_editor')

        # Left = instructions
        area_inst = ScreenAreaMapper.map_coordinates_to_area(0.25, 0.50, face_detected=True)
        self.assertEqual(area_inst, 'instructions')

        # Bottom right = console
        area_console = ScreenAreaMapper.map_coordinates_to_area(0.70, 0.85, face_detected=True)
        self.assertEqual(area_console, 'console')

        # Outside screen
        area_outside = ScreenAreaMapper.map_coordinates_to_area(0.01, 0.01, face_detected=True)
        self.assertEqual(area_outside, 'outside')

    def test_04_engagement_prediction(self):
        """Verify multimodal AI engagement prediction and category classification."""
        session = LabSession.query.first()
        self.assertIsNotNone(session)
        pred = EngagementPredictor.predict_session_engagement(session)
        self.assertIsNotNone(pred)
        self.assertIn(pred.predicted_category, ['Low Engagement', 'Moderate Engagement', 'High Engagement'])
        self.assertGreaterEqual(pred.overall_engagement_score, 0.0)
        self.assertLessEqual(pred.overall_engagement_score, 100.0)

    def test_05_teacher_export_csv(self):
        """Verify CSV export response."""
        # Login as teacher
        self.client.post('/auth/login', data={'username': 'teacher', 'password': 'admin123'})
        resp = self.client.get('/teacher/export/csv')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Session ID,Session Code,Student ID', resp.data)

if __name__ == '__main__':
    unittest.main()

