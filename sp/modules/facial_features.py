"""
Facial Features & Head Pose Module.
Provides helper utilities for head pose orientation calculations (pitch, yaw, roll)
and eye gaze directional estimation from eye and face landmark coordinates.
"""
import math

class FacialFeatureAnalyzer:
    @staticmethod
    def estimate_head_pose(landmarks: list) -> dict:
        """
        Calculates approximate pitch, yaw, and roll angles in degrees from landmarks.
        landmarks: list of [x, y, z] points or normalized coordinates.
        """
        if not landmarks or len(landmarks) < 6:
            return {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}

        try:
            # Approximate key points (nose tip, chin, left eye corner, right eye corner)
            nose = landmarks[1] if len(landmarks) > 1 else [0.5, 0.5, 0]
            chin = landmarks[152] if len(landmarks) > 152 else [0.5, 0.8, 0]
            left_eye = landmarks[33] if len(landmarks) > 33 else [0.4, 0.4, 0]
            right_eye = landmarks[263] if len(landmarks) > 263 else [0.6, 0.4, 0]

            # Yaw: Horizontal difference of nose relative to eye midpoint
            eye_mid_x = (left_eye[0] + right_eye[0]) / 2.0
            yaw = (nose[0] - eye_mid_x) * 100.0  # approximate angle degrees

            # Pitch: Vertical difference of nose relative to eyes/chin
            eye_mid_y = (left_eye[1] + right_eye[1]) / 2.0
            pitch = (nose[1] - (eye_mid_y + (chin[1] - eye_mid_y) * 0.35)) * 100.0

            # Roll: Tilt angle between left and right eyes
            dy = right_eye[1] - left_eye[1]
            dx = right_eye[0] - left_eye[0]
            roll = math.degrees(math.atan2(dy, dx)) if dx != 0 else 0.0

            return {
                'pitch': round(float(pitch), 2),
                'yaw': round(float(yaw), 2),
                'roll': round(float(roll), 2)
            }
        except Exception:
            return {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}

    @staticmethod
    def compute_gaze_direction(head_pose: dict, iris_x: float = None, iris_y: float = None) -> str:
        """
        Determines rough gaze direction ('center', 'left', 'right', 'down', 'up', 'away')
        """
        yaw = head_pose.get('yaw', 0.0)
        pitch = head_pose.get('pitch', 0.0)

        if abs(yaw) > 35 or abs(pitch) > 35:
            return 'away'
        if yaw < -15:
            return 'left'
        if yaw > 15:
            return 'right'
        if pitch > 15:
            return 'down'
        if pitch < -15:
            return 'up'
        return 'center'

