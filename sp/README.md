# AI-Based Student Behaviour Analysis and Engagement Prediction System

A full-stack AI/ML web application designed for programming laboratory sessions. The system observes multimodal indicators of student learning behaviour (eye-gaze attention, code-editing cadence, timed alert questions, and assessment performance) to estimate real-time engagement across three categories: **High Engagement**, **Moderate Engagement**, and **Low Engagement**.

---

## Key Features

1. **Dual Portals with Role-Based Access Control:**
   - **Student Portal:**
     - Session initiation with Python or C language selection.
     - Consensual webcam-based visual tracking with explicit consent controls.
     - 5 interactive programming tasks (Scratch, Jumbled statements, Fill-in-the-blank, Debugging, Output prediction).
     - Live code execution sandbox with timeouts and restricted execution safety.
     - Timed pop-up alert questions with a 5-minute countdown.
     - 10-Question final conceptual assessment with auto-grading.
     - Simple completion confirmation screen (AI internals hidden from students).
   - **Teacher Portal:**
     - Main Analytics Dashboard with key performance metrics and engagement category distribution (Doughnut charts).
     - Gaze coordinate scatter plots and screen-area attention breakdown (Code Editor %, Instructions %, Console %, Outside %).
     - Task-by-task attempts with submitted code and execution outputs.
     - Timed alert question responses and latency log.
     - Final assessment answer-by-answer review.
     - Multimodal AI engagement prediction, confidence scoring, and data quality warnings.
     - Full CSV report export and print-ready summary.

2. **Multimodal AI / ML Engagement Prediction:**
   - Fuses **Visual**, **Programming**, **Alert**, and **Assessment** feature vectors.
   - Powered by a trained **Random Forest Classifier** (`trained_models/engagement_model.pkl`) with a calibrated fallback engine.
   - Non-punitive visual safeguards: camera disconnection or declined consent does not automatically penalize student engagement.

---

## Default Demonstration Credentials

- **Teacher Account:**
  - Username: `teacher`
  - Password: `admin123`
- **Student Accounts:**
  - `student1` / `student123` (Aarav Sharma)
  - `student2` / `student123` (Priya Patel)
  - `student3` / `student123` (Rahul Verma)
  - `student4` / `student123` (Ananya Gupta)

---

## How to Run

1. **Activate Python Environment:**
   Ensure dependencies from `requirements.txt` are installed.

2. **Start the Web Application:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

3. **Run Automated Test Suite:**
   ```bash
   python test_system.py
   ```

4. **Retrain Engagement Model (Optional):**
   ```bash
   python training/train_engagement_model.py
   python training/evaluate_model.py
   ```

