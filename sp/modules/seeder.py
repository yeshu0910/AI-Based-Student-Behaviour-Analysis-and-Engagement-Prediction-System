"""
Database Seeder for Users, Tasks, Alert Questions, Assessment Questions,
and Sample Sessions for Demonstration.
"""
from datetime import datetime, timezone, timedelta
import random
import json
from database.db import db
from database.models import (
    User, AlertQuestion, AssessmentQuestion,
    LabSession, LabTaskAttempt, ProgrammingEvent, GazeObservation,
    AlertResponse, AssessmentAttempt, EngagementPrediction
)
from modules.lab_tasks import LAB_TASKS

def seed_database():
    """
    Populates database with default teachers, students, alert questions, and assessment MCQs.
    """
    # 1. Seed Users
    if not User.query.filter_by(username='teacher').first():
        teacher = User(
            username='teacher',
            email='teacher@lab.edu',
            full_name='Dr. Sunita Rao (Professor & Lab Incharge)',
            role='teacher'
        )
        teacher.set_password('admin123')
        db.session.add(teacher)

    students_data = [
        ('student1', 'student1@lab.edu', 'Aarav Sharma', 'student123'),
        ('student2', 'student2@lab.edu', 'Priya Patel', 'student123'),
        ('student3', 'student3@lab.edu', 'Rahul Verma', 'student123'),
        ('student4', 'student4@lab.edu', 'Ananya Gupta', 'student123')
    ]

    for uname, email, fname, pwd in students_data:
        if not User.query.filter_by(username=uname).first():
            st = User(username=uname, email=email, full_name=fname, role='student')
            st.set_password(pwd)
            db.session.add(st)

    db.session.commit()

    # 2. Seed Alert Questions
    alert_questions_data = [
        # Python
        ('python', 1, 'In Python, which built-in function is used to take user input from standard input?', 'input()', 'read()', 'scan()', 'get()', 'A'),
        ('python', 2, 'Which of the following creates a range of numbers from 1 up to (but not including) 6 in Python?', 'range(1, 6)', 'range(1, 5)', 'range(6)', 'list(1, 6)', 'A'),
        ('python', 3, 'Which operator is used to calculate the remainder of division (modulus) in Python?', '%', '//', '/', '**', 'A'),
        ('python', 4, 'Which keyword is used to immediately terminate and exit a loop in Python?', 'break', 'stop', 'exit', 'return', 'A'),
        ('python', 5, 'What is the outcome of [x * 2 for x in [1, 2, 3]] in Python?', '[2, 4, 6]', '[1, 2, 3, 1, 2, 3]', '[2, 2, 2]', 'SyntaxError', 'A'),
        # C
        ('c', 1, 'Which format specifier is used in scanf() to read a single integer in C?', '%d', '%f', '%c', '%s', 'A'),
        ('c', 2, 'In C, which loop structure is guaranteed to execute its block at least once?', 'do-while loop', 'for loop', 'while loop', 'switch statement', 'A'),
        ('c', 3, 'Which operator is used to obtain the memory address of a variable in C?', '&', '*', '->', '%', 'A'),
        ('c', 4, 'What is the return type of the main() function in standard C?', 'int', 'void', 'float', 'char', 'A'),
        ('c', 5, 'What does the dereference operator (*) do when applied to a pointer variable in C?', 'Accesses the value stored at the pointed address', 'Multiplies two numbers', 'Returns the memory address', 'Declares a constant', 'A')
    ]

    for lang, task_num, qtext, oa, ob, oc, od, ans in alert_questions_data:
        exists = AlertQuestion.query.filter_by(language=lang, task_number=task_num).first()
        if not exists:
            db.session.add(AlertQuestion(
                language=lang,
                task_number=task_num,
                question_text=qtext,
                option_a=oa, option_b=ob, option_c=oc, option_d=od,
                correct_option=ans
            ))

    # 3. Seed Final 10 Assessment MCQs (Python)
    python_mcqs = [
        ("What is the correct file extension for Python files?", ".py", ".python", ".pt", ".pyt", "A", "Basics"),
        ("Which of the following is an immutable data type in Python?", "Tuple", "List", "Dictionary", "Set", "A", "Data Types"),
        ("What is the output of print(type([])) in Python?", "<class 'list'>", "<class 'tuple'>", "<class 'array'>", "<class 'dict'>", "A", "Data Types"),
        ("Which keyword is used to define a function in Python?", "def", "function", "fun", "define", "A", "Functions"),
        ("What does the len() function return?", "The number of elements in an object", "The memory size in bytes", "The string representation", "The data type", "A", "Functions"),
        ("Which loop executes while a specific boolean condition remains true?", "while", "for", "do-while", "foreach", "A", "Loops"),
        ("How do you insert an element at the end of a list in Python?", "list.append(x)", "list.add(x)", "list.insert_end(x)", "list.push(x)", "A", "Data Structures"),
        ("What will be the output of print(2 ** 3)?", "8", "6", "9", "5", "A", "Operators"),
        ("Which statement is used to handle exceptions in Python?", "try ... except", "try ... catch", "do ... catch", "try ... handle", "A", "Debugging"),
        ("What is the output of bool('') in Python?", "False", "True", "None", "Error", "A", "Logic & Conditionals")
    ]

    for qtext, oa, ob, oc, od, ans, topic in python_mcqs:
        exists = AssessmentQuestion.query.filter_by(language='python', question_text=qtext).first()
        if not exists:
            db.session.add(AssessmentQuestion(
                language='python',
                question_text=qtext,
                option_a=oa, option_b=ob, option_c=oc, option_d=od,
                correct_option=ans,
                topic=topic
            ))

    # 4. Seed Final 10 Assessment MCQs (C)
    c_mcqs = [
        ("Which header file is required to use printf() and scanf() in C?", "<stdio.h>", "<stdlib.h>", "<conio.h>", "<string.h>", "A", "Basics"),
        ("What is the size of an int data type typically on a 32-bit / 64-bit architecture?", "4 bytes", "2 bytes", "8 bytes", "1 byte", "A", "Data Types"),
        ("Which symbol ends every statement in C?", "; (semicolon)", ": (colon)", ". (dot)", ", (comma)", "A", "Syntax"),
        ("How are array elements indexed in C?", "0 to n-1", "1 to n", "0 to n", "-1 to n-1", "A", "Arrays"),
        ("What is the correct syntax for an if statement in C?", "if (condition) { }", "if condition then", "if [condition]:", "if {condition}", "A", "Conditionals"),
        ("Which operator is used for logical AND in C?", "&&", "&", "AND", "||", "A", "Operators"),
        ("Which keyword is used to prevent any modification to a variable in C?", "const", "static", "volatile", "extern", "A", "Variables"),
        ("What does a function returning 'void' signify in C?", "It does not return any value", "It returns a null pointer", "It returns 0", "It is an empty function", "A", "Functions"),
        ("What will be the result of integer division: 7 / 2 in C?", "3", "3.5", "4", "3.0", "A", "Arithmetic"),
        ("What is a pointer in C?", "A variable that stores the memory address of another variable", "A keyword for looping", "A data type for fractions", "A syntax error handler", "A", "Pointers")
    ]

    for qtext, oa, ob, oc, od, ans, topic in c_mcqs:
        exists = AssessmentQuestion.query.filter_by(language='c', question_text=qtext).first()
        if not exists:
            db.session.add(AssessmentQuestion(
                language='c',
                question_text=qtext,
                option_a=oa, option_b=ob, option_c=oc, option_d=od,
                correct_option=ans,
                topic=topic
            ))

    db.session.commit()

    # 5. Populate Sample Laboratory Sessions for Demonstration
    # Create sample sessions for student1, student2, and student3 with realistic visual, programming, alert, and prediction data
    if LabSession.query.count() == 0:
        create_sample_sessions()

def create_sample_sessions():
    """
    Creates rich demonstration sessions exhibiting High, Moderate, and Low engagement
    with corresponding gaze observations, alert logs, and predictions.
    """
    profiles = [
        {
            'username': 'student1',
            'lang': 'python',
            'category': 'High Engagement',
            'visual_score': 88.0,
            'prog_score': 92.0,
            'alert_score': 85.0,
            'assess_score': 90.0,
            'overall': 89.2,
            'conf': 0.94,
            'face_pct': 92.0,
            'editor_pct': 74.0,
            'edits': 45,
            'keystrokes': 320,
            'alert_ans': 3,
            'alert_cor': 3,
            'assess_val': 9
        },
        {
            'username': 'student2',
            'lang': 'python',
            'category': 'Moderate Engagement',
            'visual_score': 62.0,
            'prog_score': 58.0,
            'alert_score': 60.0,
            'assess_score': 70.0,
            'overall': 61.5,
            'conf': 0.88,
            'face_pct': 76.0,
            'editor_pct': 52.0,
            'edits': 24,
            'keystrokes': 180,
            'alert_ans': 2,
            'alert_cor': 1,
            'assess_val': 7
        },
        {
            'username': 'student3',
            'lang': 'c',
            'category': 'Low Engagement',
            'visual_score': 32.0,
            'prog_score': 30.0,
            'alert_score': 25.0,
            'assess_score': 40.0,
            'overall': 32.8,
            'conf': 0.85,
            'face_pct': 42.0,
            'editor_pct': 28.0,
            'edits': 8,
            'keystrokes': 45,
            'alert_ans': 1,
            'alert_cor': 0,
            'assess_val': 4
        }
    ]

    now = datetime.now(timezone.utc)
    for idx, p in enumerate(profiles):
        user = User.query.filter_by(username=p['username']).first()
        if not user:
            continue

        sess_code = f"DEMO-SESSION-00{idx+1}"
        start = now - timedelta(hours=idx*3 + 1, minutes=45)
        end = start + timedelta(minutes=42)

        session = LabSession(
            student_id=user.id,
            session_code=sess_code,
            language=p['lang'],
            start_time=start,
            end_time=end,
            status='completed',
            camera_consent=True
        )
        db.session.add(session)
        db.session.flush()

        # Add 5 task attempts
        lang_tasks = LAB_TASKS.get(p['lang'], LAB_TASKS['python'])
        for t_num in range(1, 6):
            spec = lang_tasks.get(t_num, {})
            attempt = LabTaskAttempt(
                session_id=session.id,
                task_number=t_num,
                task_title=spec.get('title', f'Task {t_num}'),
                task_type=spec.get('type', 'scratch'),
                code_submitted=spec.get('starter_code', ''),
                execution_output=spec.get('expected_output', ''),
                is_passed=(p['category'] != 'Low Engagement' or t_num <= 2),
                edits_count=p['edits'] // 5 + random.randint(1, 4),
                keystrokes_count=p['keystrokes'] // 5 + random.randint(5, 20),
                time_spent_seconds=random.randint(240, 480),
                start_time=start + timedelta(minutes=(t_num-1)*7),
                submit_time=start + timedelta(minutes=t_num*7),
                status='completed'
            )
            db.session.add(attempt)

        # Generate Gaze Observations
        for g_idx in range(40):
            g_time = start + timedelta(minutes=g_idx)
            face_det = random.random() < (p['face_pct'] / 100.0)
            if face_det:
                is_editor = random.random() < (p['editor_pct'] / 100.0)
                if is_editor:
                    gx = random.uniform(0.45, 0.90)
                    gy = random.uniform(0.15, 0.60)
                    area = 'code_editor'
                else:
                    sub_area = random.choice(['instructions', 'console', 'outside'])
                    area = sub_area
                    gx = random.uniform(0.1, 0.4) if area == 'instructions' else random.uniform(0.45, 0.9)
                    gy = random.uniform(0.7, 0.95) if area == 'console' else 0.02
            else:
                gx, gy, area = 0.5, 0.5, 'unknown'

            obs = GazeObservation(
                session_id=session.id,
                timestamp=g_time,
                face_detected=face_det,
                head_pose_pitch=round(random.uniform(-10, 10), 1),
                head_pose_yaw=round(random.uniform(-15, 15), 1),
                head_pose_roll=round(random.uniform(-5, 5), 1),
                gaze_x=round(gx, 3),
                gaze_y=round(gy, 3),
                screen_area=area,
                fixation_duration=round(random.uniform(0.8, 3.5), 1)
            )
            db.session.add(obs)

        # Generate Alert Responses
        alerts = AlertQuestion.query.filter_by(language=p['lang']).limit(3).all()
        for a_idx, alert in enumerate(alerts):
            status = 'answered' if a_idx < p['alert_ans'] else 'timed_out'
            is_cor = (status == 'answered' and a_idx < p['alert_cor'])
            resp = AlertResponse(
                session_id=session.id,
                alert_id=alert.id,
                displayed_at=start + timedelta(minutes=10 * (a_idx + 1)),
                responded_at=start + timedelta(minutes=10 * (a_idx + 1), seconds=35),
                student_answer=alert.correct_option if is_cor else 'B',
                is_correct=is_cor,
                response_time_seconds=35.0 if status == 'answered' else 300.0,
                status=status
            )
            db.session.add(resp)

        # Generate Assessment Attempt
        attempt_assm = AssessmentAttempt(
            session_id=session.id,
            student_id=user.id,
            total_score=p['assess_val'],
            max_score=10,
            answers_json=json.dumps({"1": "A", "2": "A", "3": "A"}),
            start_time=end - timedelta(minutes=12),
            submit_time=end,
            completion_time_seconds=720,
            status='completed'
        )
        db.session.add(attempt_assm)

        # Add Engagement Prediction
        summary_payload = {
            'indicators': [
                f"Visual attention on code/instructions: {p['editor_pct']}% of session duration.",
                f"Completed 5/5 tasks with {p['edits']} edits and {p['keystrokes']} keystrokes.",
                f"Answered {p['alert_ans']} alert queries with {p['alert_cor']} correct.",
                f"Final assessment score: {p['assess_val']}/10."
            ],
            'warnings': [] if p['category'] != 'Low Engagement' else ["Frequent off-screen gaze directions and low interaction keystrokes observed."]
        }
        pred = EngagementPrediction(
            session_id=session.id,
            student_id=user.id,
            visual_score=p['visual_score'],
            programming_score=p['prog_score'],
            alert_score=p['alert_score'],
            assessment_score=p['assess_score'],
            overall_engagement_score=p['overall'],
            predicted_category=p['category'],
            confidence=p['conf'],
            feature_summary_json=json.dumps(summary_payload),
            created_at=end
        )
        db.session.add(pred)

    db.session.commit()

