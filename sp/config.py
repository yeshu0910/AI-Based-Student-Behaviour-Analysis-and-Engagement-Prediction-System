import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'anti-gravity-super-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'database', 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    # Lab Session Config
    ALERT_TIMEOUT_SECONDS = 300 # 5 minutes
    ALERT_TRIGGER_INTERVAL = 120 # every 2 minutes an alert may trigger
    MAX_TASKS = 5
    ASSESSMENT_QUESTIONS_COUNT = 10
    
    # Paths
    TRAINED_MODELS_DIR = os.path.join(BASE_DIR, 'trained_models')
    DATASETS_DIR = os.path.join(BASE_DIR, 'datasets')
    RECORDS_DIR = os.path.join(BASE_DIR, 'records')

