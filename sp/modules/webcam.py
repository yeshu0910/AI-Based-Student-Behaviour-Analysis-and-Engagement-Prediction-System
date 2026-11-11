"""
Webcam Management & Frame Feature Processing.
Receives client-side feature snapshots or frames, extracts face landmarks,
and computes gaze coordinates safely without storing intrusive raw videos.
"""
import base64
import numpy as np
import cv2

class WebcamProcessor:
    @staticmethod
    def process_base64_frame(data_url: str):
        """
        Safely extracts basic OpenCV facial detection from a base64 encoded JPEG/PNG frame.
        Returns face_detected, bounding_box, approximate gaze_x, gaze_y.
        """
        if not data_url or ',' not in data_url:
            return {'face_detected': False, 'gaze_x': 0.5, 'gaze_y': 0.5, 'head_pose': {'pitch': 0, 'yaw': 0, 'roll': 0}}

        try:
            header, encoded = data_url.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return {'face_detected': False, 'gaze_x': 0.5, 'gaze_y': 0.5, 'head_pose': {'pitch': 0, 'yaw': 0, 'roll': 0}}

            h, w, _ = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use OpenCV Haar cascade face detector as dependable baseline
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.py'
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

            if len(faces) == 0:
                return {
                    'face_detected': False,
                    'gaze_x': 0.5,
                    'gaze_y': 0.5,
                    'head_pose': {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0}
                }

            # Pick primary face
            (x, y, fw, fh) = faces[0]
            face_center_x = (x + fw / 2.0) / w
            face_center_y = (y + fh / 2.0) / h

            # Screen coordinates are inverted horizontally for webcams (mirror effect)
            gaze_x = round(1.0 - face_center_x, 3)
            gaze_y = round(face_center_y, 3)

            # Approximate yaw and pitch from face bounding displacement
            yaw = round((face_center_x - 0.5) * -60.0, 1)
            pitch = round((face_center_y - 0.5) * 60.0, 1)

            return {
                'face_detected': True,
                'gaze_x': gaze_x,
                'gaze_y': gaze_y,
                'head_pose': {'pitch': pitch, 'yaw': yaw, 'roll': 0.0}
            }
        except Exception:
            return {'face_detected': False, 'gaze_x': 0.5, 'gaze_y': 0.5, 'head_pose': {'pitch': 0, 'yaw': 0, 'roll': 0}}

