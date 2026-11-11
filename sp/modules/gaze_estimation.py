"""
Gaze Estimation and Screen Attention Mapping Module.
Classifies normalized gaze coordinates into relevant workspace screen areas:
- Code Editor
- Question / Instructions Area
- Output / Console Area
- Outside Screen / Looking Away
- Unknown / Face Unavailable
"""

class ScreenAreaMapper:
    # Normalized layout boundaries (X: 0.0=left, 1.0=right; Y: 0.0=top, 1.0=bottom)
    # Desktop split layout:
    # Left column: Instructions / Alert modal (X: 0.0 to 0.40)
    # Right column top: Code editor (X: 0.40 to 1.0, Y: 0.0 to 0.65)
    # Right column bottom: Output console / Run controls (X: 0.40 to 1.0, Y: 0.65 to 1.0)
    
    @staticmethod
    def map_coordinates_to_area(gaze_x: float, gaze_y: float, face_detected: bool = True) -> str:
        """
        Maps normalized coordinates (0.0 to 1.0) to screen regions.
        Handles bounds checks for looking outside screen.
        """
        if not face_detected:
            return 'unknown'

        if gaze_x is None or gaze_y is None:
            return 'unknown'

        # Off-screen boundaries
        if gaze_x < 0.05 or gaze_x > 0.95 or gaze_y < 0.05 or gaze_y > 0.95:
            return 'outside'

        # Left side: Instructions & Task details
        if 0.05 <= gaze_x <= 0.42:
            return 'instructions'

        # Right side: Code editor and console
        if 0.42 < gaze_x <= 0.95:
            if gaze_y <= 0.68:
                return 'code_editor'
            else:
                return 'console'

        return 'unknown'

    @staticmethod
    def calculate_fixation_and_attention(observations: list) -> dict:
        """
        Analyzes a list of GazeObservation records to compute:
        - Face detection %
        - Area percentage breakdown (editor %, instructions %, console %, outside %, unknown %)
        - Average fixation duration
        - Head pose stability (pitch/yaw variance)
        """
        total = len(observations)
        if total == 0:
            return {
                'total_observations': 0,
                'face_visibility_pct': 0.0,
                'editor_pct': 0.0,
                'instructions_pct': 0.0,
                'console_pct': 0.0,
                'outside_pct': 0.0,
                'unknown_pct': 100.0,
                'avg_fixation_seconds': 0.0,
                'data_quality_warning': 'No visual observations recorded (camera may have been declined or unavailable).'
            }

        faces_detected = sum(1 for o in observations if o.face_detected)
        area_counts = {'code_editor': 0, 'instructions': 0, 'console': 0, 'outside': 0, 'unknown': 0}
        total_fixation = 0.0

        for o in observations:
            area = o.screen_area if o.screen_area in area_counts else 'unknown'
            area_counts[area] += 1
            if o.fixation_duration:
                total_fixation += o.fixation_duration

        face_pct = round((faces_detected / total) * 100.0, 1)
        editor_pct = round((area_counts['code_editor'] / total) * 100.0, 1)
        instructions_pct = round((area_counts['instructions'] / total) * 100.0, 1)
        console_pct = round((area_counts['console'] / total) * 100.0, 1)
        outside_pct = round((area_counts['outside'] / total) * 100.0, 1)
        unknown_pct = round((area_counts['unknown'] / total) * 100.0, 1)
        avg_fix = round(total_fixation / total, 2) if total > 0 else 0.0

        warning = None
        if face_pct < 40.0:
            warning = "Face was not detected for >60% of the session. Check lighting or user position."

        return {
            'total_observations': total,
            'face_visibility_pct': face_pct,
            'editor_pct': editor_pct,
            'instructions_pct': instructions_pct,
            'console_pct': console_pct,
            'outside_pct': outside_pct,
            'unknown_pct': unknown_pct,
            'avg_fixation_seconds': avg_fix,
            'data_quality_warning': warning
        }

