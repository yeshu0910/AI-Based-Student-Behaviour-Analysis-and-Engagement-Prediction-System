"""
Assessment Module.
Handles the final 10-question MCQ assessment testing core programming competencies
in Python and C, score calculation, and attempt record keeping.
"""
from datetime import datetime, timezone
import json
from database.db import db
from database.models import AssessmentQuestion, AssessmentAttempt

class AssessmentManager:
    @staticmethod
    def get_questions_for_session(language: str, limit: int = 10):
        """
        Retrieves 10 assessment questions matching the session programming language.
        """
        return AssessmentQuestion.query.filter_by(
            language=language.lower()
        ).limit(limit).all()

    @staticmethod
    def submit_assessment(session_id: int, student_id: int, answers: dict, start_time: datetime = None) -> AssessmentAttempt:
        """
        Calculates score against correct answers, stores json responses and duration.
        """
        attempt = AssessmentAttempt.query.filter_by(session_id=session_id).first()
        now = datetime.now(timezone.utc)
        
        if not attempt:
            attempt = AssessmentAttempt(
                session_id=session_id,
                student_id=student_id,
                start_time=start_time or now
            )
            db.session.add(attempt)

        score = 0
        total_questions = 0

        # Validate answers against DB questions
        for q_id_str, selected_option in answers.items():
            try:
                q_id = int(q_id_str)
                question = AssessmentQuestion.query.get(q_id)
                if question:
                    total_questions += 1
                    if selected_option and selected_option.strip().upper() == question.correct_option.strip().upper():
                        score += 1
            except ValueError:
                continue

        # Duration
        start = attempt.start_time.replace(tzinfo=timezone.utc) if attempt.start_time.tzinfo is None else attempt.start_time
        duration = int((now - start).total_seconds())

        attempt.total_score = score
        attempt.max_score = total_questions or 10
        attempt.answers_json = json.dumps(answers)
        attempt.submit_time = now
        attempt.completion_time_seconds = max(0, duration)
        attempt.status = 'completed'

        db.session.commit()
        return attempt

    @staticmethod
    def get_attempt_details(session_id: int):
        """
        Retrieves full breakdown of questions, student answers, and correctness for teacher view.
        """
        attempt = AssessmentAttempt.query.filter_by(session_id=session_id).first()
        if not attempt:
            return None

        answers_dict = attempt.get_answers_dict()
        detailed_questions = []

        for q_id_str, student_opt in answers_dict.items():
            try:
                q = AssessmentQuestion.query.get(int(q_id_str))
                if q:
                    detailed_questions.append({
                        'question': q.question_text,
                        'topic': q.topic,
                        'options': {'A': q.option_a, 'B': q.option_b, 'C': q.option_c, 'D': q.option_d},
                        'student_answer': student_opt,
                        'correct_answer': q.correct_option,
                        'is_correct': (student_opt.upper() == q.correct_option.upper()) if student_opt else False
                    })
            except ValueError:
                continue

        return {
            'attempt': attempt,
            'score': attempt.total_score,
            'max_score': attempt.max_score,
            'percentage': round((attempt.total_score / max(1, attempt.max_score)) * 100.0, 1),
            'duration_minutes': round(attempt.completion_time_seconds / 60.0, 1),
            'questions_breakdown': detailed_questions
        }

