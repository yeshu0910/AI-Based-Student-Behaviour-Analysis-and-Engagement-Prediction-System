"""
Model Evaluation and Metrics Reporting.
Outputs Accuracy, Precision, Recall, Macro F1, and Confusion Matrix.
"""
import os
import sys
import json
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def evaluate_saved_model():
    model_path = os.path.join(Config.TRAINED_MODELS_DIR, 'engagement_model.pkl')
    features_csv = os.path.join(Config.DATASETS_DIR, 'custom_lab_data', 'session_features.csv')
    labels_csv = os.path.join(Config.DATASETS_DIR, 'custom_lab_data', 'session_labels.csv')

    if not os.path.exists(model_path) or not os.path.exists(features_csv):
        print("Model or dataset not found. Please run training/train_engagement_model.py first.")
        return

    model = joblib.load(model_path)
    X = pd.read_csv(features_csv)
    y = pd.read_csv(labels_csv)['engagement_label']

    y_pred = model.predict(X)
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average='macro')
    cm = confusion_matrix(y, y_pred, labels=['Low Engagement', 'Moderate Engagement', 'High Engagement'])

    print("=" * 60)
    print("ENGAGEMENT PREDICTION MODEL EVALUATION REPORT")
    print("=" * 60)
    print(f"Overall Accuracy : {acc * 100:.2f}%")
    print(f"Macro F1-Score   : {f1:.4f}")
    print("\nClassification Report:\n")
    print(classification_report(y, y_pred))
    print("\nConfusion Matrix (Low, Moderate, High):\n")
    print(cm)
    print("=" * 60)

if __name__ == '__main__':
    evaluate_saved_model()

