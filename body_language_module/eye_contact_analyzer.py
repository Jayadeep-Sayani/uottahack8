"""
Eye Contact Analysis Module

Analyzes eye contact with camera and eye opening naturalness.
Uses MediaPipe Face Mesh for facial landmark detection.
"""

import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
from typing import Dict, Tuple


class EyeContactAnalyzer:
    """
    Analyzes eye contact and eye opening in video files.
    Evaluates if person is looking at camera and if eyes are naturally open.
    """
    
    def __init__(self):
        """Initialize MediaPipe face mesh for eye detection."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Metrics tracking
        self.eye_contact_scores = []
        self.eye_opening_scores = []
        self.combined_scores = []
    
    def analyze_video(self, video_path: str) -> Dict:
        """
        Analyze eye contact in a video file.
        
        Args:
            video_path: Path to the MP4 video file
        
        Returns:
            Dictionary with eye contact analysis results
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if video_path.suffix.lower() != ".mp4":
            raise ValueError(f"Expected MP4 file, got: {video_path.suffix}")
        
        # Reset metrics
        self.eye_contact_scores = []
        self.eye_opening_scores = []
        self.combined_scores = []
        
        # Open video file
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            raise ValueError("Could not read video file")
        
        frame_count = 0
        processed_frames = 0
        
        print(f"Analyzing eye contact: {video_path.name}")
        print(f"Total frames: {total_frames}\n")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Process every Nth frame to speed up analysis
            if frame_count % 5 != 0:
                continue
            
            # Analyze frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                processed_frames += 1
                self._evaluate_frame(results.multi_face_landmarks[0])
        
        cap.release()
        
        # Compile results
        results = self._compile_analysis(processed_frames)
        
        return results
    
    def _evaluate_frame(self, face_landmarks):
        """
        Evaluate eye contact and eye opening for a single frame.
        
        Args:
            face_landmarks: MediaPipe face mesh landmarks
        """
        eye_contact_score, eye_opening_score = self._calculate_eye_metrics(face_landmarks)
        self.eye_contact_scores.append(eye_contact_score)
        self.eye_opening_scores.append(eye_opening_score)
        
        # Combined score (weighted average)
        combined = eye_contact_score * 0.6 + eye_opening_score * 0.4
        self.combined_scores.append(combined)
    
    def _calculate_eye_metrics(self, face_landmarks) -> Tuple[float, float]:
        """
        Calculate eye contact and eye opening scores.
        
        Args:
            face_landmarks: MediaPipe face mesh landmarks
        
        Returns:
            Tuple of (eye_contact_score, eye_opening_score)
        """
        # Key face mesh indices
        LEFT_EYE_INNER = 133
        LEFT_EYE_OUTER = 130
        RIGHT_EYE_INNER = 362
        RIGHT_EYE_OUTER = 359
        LEFT_EYE_UP = 159
        LEFT_EYE_DOWN = 145
        RIGHT_EYE_UP = 386
        RIGHT_EYE_DOWN = 374
        
        landmarks = face_landmarks.landmark
        
        # ========== EYE CONTACT DETECTION ==========
        # Good eye contact = looking at camera (eyes centered)
        # Measure horizontal position of eyes
        
        left_eye_x = landmarks[LEFT_EYE_INNER].x
        right_eye_x = landmarks[RIGHT_EYE_INNER].x
        avg_eye_x = (left_eye_x + right_eye_x) / 2
        
        # Distance from center (0.5 in normalized coords)
        # 0.5 = looking straight at camera
        eye_horizontal_deviation = abs(avg_eye_x - 0.5)
        
        if eye_horizontal_deviation < 0.05:
            eye_contact_score = 1.0  # Perfect eye contact
        elif eye_horizontal_deviation < 0.15:
            eye_contact_score = 0.7  # Good eye contact
        elif eye_horizontal_deviation < 0.25:
            eye_contact_score = 0.4  # Moderate eye contact
        else:
            eye_contact_score = 0.1  # Poor eye contact (looking away)
        
        # ========== EYE OPENING DETECTION ==========
        # Good = natural eye opening (not closed, not too wide)
        # Measure vertical distance between upper and lower eyelids
        
        left_eye_vertical = abs(landmarks[LEFT_EYE_UP].y - landmarks[LEFT_EYE_DOWN].y)
        right_eye_vertical = abs(landmarks[RIGHT_EYE_UP].y - landmarks[RIGHT_EYE_DOWN].y)
        avg_eye_opening = (left_eye_vertical + right_eye_vertical) / 2
        
        # Good eye opening: moderate distance (0.035-0.065 is optimal)
        if avg_eye_opening < 0.015:
            eye_opening_score = 0.1  # Eyes too closed
        elif avg_eye_opening < 0.025:
            eye_opening_score = 0.5  # Eyes closed
        elif avg_eye_opening < 0.035:
            eye_opening_score = 0.75  # Slightly closed
        elif avg_eye_opening < 0.065:
            eye_opening_score = 1.0  # Natural eye opening (GOOD)
        elif avg_eye_opening < 0.10:
            eye_opening_score = 0.7  # Eyes slightly too wide
        else:
            eye_opening_score = 0.3  # Eyes too wide open (shocked/surprised)
        
        return eye_contact_score, eye_opening_score
    
    def _compile_analysis(self, processed_frames: int) -> Dict:
        """
        Compile eye contact analysis results into a summary.
        
        Args:
            processed_frames: Number of frames processed
        
        Returns:
            Dictionary with eye contact analysis results
        """
        if processed_frames == 0:
            return {
                "status": "No face detected",
                "overall_score": 0,
                "assessment": "UNABLE_TO_ANALYZE",
                "details": {}
            }
        
        # Calculate average scores
        avg_eye_contact = np.mean(self.eye_contact_scores) if self.eye_contact_scores else 0
        avg_eye_opening = np.mean(self.eye_opening_scores) if self.eye_opening_scores else 0
        overall_score = np.mean(self.combined_scores) if self.combined_scores else 0
        
        # Determine assessment
        if overall_score >= 0.75:
            assessment = "EXCELLENT"
            interpretation = "Excellent eye contact - strong direct gaze and natural eye opening"
        elif overall_score >= 0.60:
            assessment = "GOOD"
            interpretation = "Good eye contact - mostly looking at camera with natural eye expression"
        elif overall_score >= 0.40:
            assessment = "FAIR"
            interpretation = "Fair eye contact - occasional looking away or unnatural eye opening"
        else:
            assessment = "POOR"
            interpretation = "Poor eye contact - frequently looking away or eyes closed/too wide"
        
        # Generate recommendations
        recommendations = []
        if avg_eye_contact < 0.6:
            recommendations.append("Improve eye contact - maintain focus on the camera")
        if avg_eye_opening < 0.6:
            recommendations.append("Adjust eye opening - keep eyes naturally open, not too closed or wide")
        if not recommendations:
            recommendations.append("Maintain your excellent eye contact!")
        
        return {
            "status": "Analysis Complete",
            "overall_score": round(overall_score, 3),
            "assessment": assessment,
            "interpretation": interpretation,
            "details": {
                "eye_contact_score": round(avg_eye_contact, 3),
                "eye_opening_score": round(avg_eye_opening, 3),
                "frames_analyzed": processed_frames
            },
            "recommendations": recommendations
        }


def analyze_eye_contact(video_path: str) -> Dict:
    """
    Convenience function to analyze eye contact in a video.
    
    Args:
        video_path: Path to the MP4 video file
    
    Returns:
        Dictionary with eye contact analysis results
    """
    analyzer = EyeContactAnalyzer()
    return analyzer.analyze_video(video_path)
