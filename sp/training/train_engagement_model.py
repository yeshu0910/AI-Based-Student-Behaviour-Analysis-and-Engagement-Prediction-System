"""
Model Training Pipeline for Multimodal Engagement Prediction.
Synthesizes and preprocesses laboratory features (Visual, Programming, Alert, Assessment),
trains a Random Forest classifier with stratified Train/Val/Test splits,
computes precision, recall, macro F1-score, and confusion matrix,
and serializes the trained model artifact to trained_models/.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

def generate_synthetic_lab_dataset(num_samples: int = 400):
    """
    Generates realistic multimodal laboratory interaction datasets based on empirical
    classroom parameters and distributions.
    """
    np.random.seed(42)
    data = []

    for _ in range(num_samples):
        # Sample an underlying latent engagement tendency: 0=Low, 1=Moderate, 2=High
        latent = np.random.choice([0, 1, 2], p=[0.25, 0.45, 0.30])

        if latent == 2:  # High Engagement
            face_visibility = np.clip(np.random.normal(88, 7), 50, 100)
            editor_attention = np.clip(np.random.normal(75, 8), 45, 95)
            outside_attention = np.clip(np.random.normal(6, 4), 0, 20)
            avg_fixation = np.clip(np.random.normal(2.6, 0.5), 1.0, 5.0)
            edits = int(np.clip(np.random.normal(42, 10), 15, 80))
            keystrokes = int(np.clip(np.random.normal(320, 50), 120, 600))
            tasks_completed = np.random.choice([4, 5], p=[0.15, 0.85])
            idle_events = int(np.clip(np.random.normal(2, 1), 0, 6))
            alerts_answered = np.random.choice([2, 3], p=[0.2, 0.8])
            alerts_correct = np.clip(alerts_answered - np.random.choice([0, 1], p=[0.8, 0.2]), 0, 3)
            assessment_score = int(np.clip(np.random.normal(8.5, 1.2), 6, 10))
            label = 'High Engagement'

        elif latent == 1:  # Moderate Engagement
            face_visibility = np.clip(np.random.normal(74, 10), 35, 95)
            editor_attention = np.clip(np.random.normal(54, 10), 30, 75)
            outside_attention = np.clip(np.random.normal(16, 6), 5, 35)
            avg_fixation = np.clip(np.random.normal(1.8, 0.4), 0.8, 3.5)
            edits = int(np.clip(np.random.normal(22, 7), 8, 45))
            keystrokes = int(np.clip(np.random.normal(170, 35), 60, 300))
            tasks_completed = np.random.choice([3, 4, 5], p=[0.25, 0.55, 0.20])
            idle_events = int(np.clip(np.random.normal(5, 2), 1, 10))
            alerts_answered = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
            alerts_correct = np.clip(alerts_answered - np.random.choice([0, 1], p=[0.5, 0.5]), 0, 3)
            assessment_score = int(np.clip(np.random.normal(6.5, 1.4), 4, 9))
            label = 'Moderate Engagement'

        else:  # Low Engagement
            face_visibility = np.clip(np.random.normal(48, 15), 10, 80)
            editor_attention = np.clip(np.random.normal(32, 12), 10, 50)
            outside_attention = np.clip(np.random.normal(36, 12), 15, 70)
            avg_fixation = np.clip(np.random.normal(1.1, 0.4), 0.4, 2.2)
            edits = int(np.clip(np.random.normal(8, 4), 1, 20))
            keystrokes = int(np.clip(np.random.normal(55, 25), 10, 120))
            tasks_completed = np.random.choice([1, 2, 3], p=[0.45, 0.40, 0.15])
            idle_events = int(np.clip(np.random.normal(11, 3), 4, 20))
            alerts_answered = np.random.choice([0, 1], p=[0.5, 0.5])
            alerts_correct = 0 if alerts_answered == 0 else np.random.choice([0, 1], p=[0.7, 0.3])
            assessment_score = int(np.clip(np.random.normal(3.8, 1.3), 1, 6))
            label = 'Low Engagement'

        data.append({
            'face_visibility_pct': face_visibility,
            'editor_attention_pct': editor_attention,
            'outside_attention_pct': outside_attention,
            'avg_fixation_seconds': avg_fixation,
            'edits_count': edits,
            'keystrokes_count': keystrokes,
            'tasks_completed': tasks_completed,
            'idle_events_count': idle_events,
            'alerts_answered': alerts_answered,
            'alerts_correct': alerts_correct,
            'assessment_score': assessment_score,
            'engagement_label': label
        })

    df = pd.DataFrame(data)
    return df

def train_and_save_model():
    os.makedirs(os.path.join(Config.DATASETS_DIR, 'custom_lab_data'), exist_ok=True)
    os.makedirs(Config.TRAINED_MODELS_DIR, exist_ok=True)

    df = generate_synthetic_lab_dataset(500)
    
    # Save CSVs
    features_csv = os.path.join(Config.DATASETS_DIR, 'custom_lab_data', 'session_features.csv')
    labels_csv = os.path.join(Config.DATASETS_DIR, 'custom_lab_data', 'session_labels.csv')
    df.drop(columns=['engagement_label']).to_csv(features_csv, index=False)
    df[['engagement_label']].to_csv(labels_csv, index=False)

    feature_cols = [
        'face_visibility_pct', 'editor_attention_pct', 'outside_attention_pct',
        'avg_fixation_seconds', 'edits_count', 'keystrokes_count',
        'tasks_completed', 'idle_events_count', 'alerts_answered',
        'alerts_correct', 'assessment_score'
    ]

    X = df[feature_cols]
    y = df['engagement_label']

    # Train / Test split (80 / 20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    report = classification_report(y_test, y_pred, output_dict=True)
    c_matrix = confusion_matrix(y_test, y_pred, labels=['Low Engagement', 'Moderate Engagement', 'High Engagement']).tolist()

    # Feature Importances
    importances = dict(zip(feature_cols, [round(float(v), 4) for v in clf.feature_importances_]))

    # Save model and metadata
    model_path = os.path.join(Config.TRAINED_MODELS_DIR, 'engagement_model.pkl')
    meta_path = os.path.join(Config.TRAINED_MODELS_DIR, 'model_metadata.json')

    joblib.dump(clf, model_path)
    
    metadata = {
        'model_name': 'RandomForestClassifier',
        'n_estimators': 100,
        'test_accuracy': round(float(acc), 4),
        'macro_f1': round(float(f1), 4),
        'feature_names': feature_cols,
        'feature_importances': importances,
        'confusion_matrix': c_matrix,
        'classification_report': report,
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }

    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Model trained successfully! Test Accuracy: {acc*100:.2f}%, Macro F1: {f1:.4f}")
    return metadata

if __name__ == '__main__':
    train_and_save_model()
