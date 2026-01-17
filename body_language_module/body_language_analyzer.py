"""
Body Language Analysis Module

Analyzes video files to determine if the user has good or bad body language.
Uses MediaPipe for pose estimation and OpenCV for video processing.
"""

import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List


class BodyLanguageAnalyzer:
    """
    Analyzes body language in video files using pose estimation.
    Evaluates posture, shoulder alignment, head position, and gesture patterns.
    """
    
    def __init__(self):
        """Initialize MediaPipe pose estimator."""
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Metrics tracking
        self.posture_scores = []
        self.shoulder_alignment_scores = []
        self.head_position_scores = []
        self.gesture_scores = []
        self.confidence_scores = []
    
    def analyze_video(self, video_path: str) -> Dict:
        """
        Analyze body language in a video file.
        
        Args:
            video_path: Path to the MP4 video file
        
        Returns:
            Dictionary with analysis results
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if video_path.suffix.lower() != ".mp4":
            raise ValueError(f"Expected MP4 file, got: {video_path.suffix}")
        
        # Reset metrics
        self.posture_scores = []
        self.shoulder_alignment_scores = []
        self.head_position_scores = []
        self.gesture_scores = []
        self.confidence_scores = []
        
        # Open video file
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            raise ValueError("Could not read video file")
        
        frame_count = 0
        processed_frames = 0
        
        print(f"Analyzing video: {video_path.name}")
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
            results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            if results.pose_landmarks:
                processed_frames += 1
                self._evaluate_frame(results.pose_landmarks)
        
        cap.release()
        
        # Compile results
        results = self._compile_analysis(processed_frames)
        
        return results
    
    def _evaluate_frame(self, landmarks):
        """
        Evaluate a single frame's pose landmarks.
        
        Args:
            landmarks: MediaPipe pose landmarks
        """
        # Extract key points (access via .landmark to get the list)
        landmark_list = landmarks.landmark
        nose = landmark_list[0]
        left_shoulder = landmark_list[11]
        right_shoulder = landmark_list[12]
        left_hip = landmark_list[23]
        right_hip = landmark_list[24]
        left_ear = landmark_list[7]
        right_ear = landmark_list[8]
        left_wrist = landmark_list[9]
        right_wrist = landmark_list[10]
        
        # Check visibility
        visible_points = sum(1 for lm in landmark_list if lm.visibility > 0.5)
        self.confidence_scores.append(visible_points / len(landmark_list))
        
        # 1. Evaluate Posture (back straightness)
        posture_score = self._evaluate_posture(left_shoulder, right_shoulder, left_hip, right_hip, nose)
        self.posture_scores.append(posture_score)
        
        # 2. Evaluate Shoulder Alignment
        shoulder_score = self._evaluate_shoulder_alignment(left_shoulder, right_shoulder)
        self.shoulder_alignment_scores.append(shoulder_score)
        
        # 3. Evaluate Head Position
        head_score = self._evaluate_head_position(nose, left_shoulder, right_shoulder, left_ear, right_ear)
        self.head_position_scores.append(head_score)
        
        # 4. Evaluate Gestures
        gesture_score = self._evaluate_gestures(left_wrist, right_wrist, left_shoulder, right_shoulder)
        self.gesture_scores.append(gesture_score)
    
    def _evaluate_posture(self, left_shoulder, right_shoulder, left_hip, right_hip, nose):
        """
        Evaluate posture straightness.
        Good posture: straight spine, shoulders aligned with hips, head neutral.
        Bad posture: slouching, leaning, forward head.
        VERY STRICT SCORING.
        """
        # Calculate spine and shoulder centers
        shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_center_x = (left_hip.x + right_hip.x) / 2
        hip_center_y = (left_hip.y + right_hip.y) / 2
        
        # 1. Check vertical alignment (spine should be VERY vertical)
        horizontal_offset = abs(shoulder_center_x - hip_center_x)
        vertical_distance = abs(shoulder_center_y - hip_center_y)
        
        if vertical_distance < 0.01:  # Invalid pose
            return 0.5
        
        # Extremely strict thresholds for leaning
        # Good: < 0.02, otherwise increasingly bad
        lean_ratio = horizontal_offset / vertical_distance
        if lean_ratio < 0.02:
            lean_penalty = 0  # Excellent alignment
        elif lean_ratio < 0.05:
            lean_penalty = 0.2  # Acceptable
        elif lean_ratio < 0.1:
            lean_penalty = 0.5  # Noticeable lean
        else:
            lean_penalty = 0.9  # Very bad lean
        
        # 2. Check for forward head posture (EXTREMELY strict)
        # Perfect alignment: head centered with shoulders
        head_forward_offset = abs(nose.x - shoulder_center_x)
        if head_forward_offset < 0.02:
            forward_penalty = 0  # Perfect
        elif head_forward_offset < 0.05:
            forward_penalty = 0.3  # Tiny bit forward
        elif head_forward_offset < 0.1:
            forward_penalty = 0.6  # Noticeable forward head
        else:
            forward_penalty = 0.95  # Severe forward head posture
        
        # 3. Check for slouching (EXTREMELY strict)
        # Shoulders MUST be above hips for good posture
        shoulder_hip_diff = shoulder_center_y - hip_center_y
        if shoulder_hip_diff < -0.05:  # Shoulders well above hips
            slouch_penalty = 0  # Excellent
        elif shoulder_hip_diff < 0:  # Shoulders slightly above hips
            slouch_penalty = 0.1  # Good
        elif shoulder_hip_diff < 0.02:  # Shoulders at same level
            slouch_penalty = 0.5  # Noticeable slouch
        elif shoulder_hip_diff < 0.08:  # Shoulders below hips
            slouch_penalty = 0.75  # Significant slouch
        else:  # Major slouch
            slouch_penalty = 0.95
        
        # Calculate final posture score with heavy penalties
        posture_score = max(0, 1.0 - lean_penalty - forward_penalty - slouch_penalty)
        
        return min(1.0, posture_score)
    
    def _evaluate_shoulder_alignment(self, left_shoulder, right_shoulder):
        """
        Evaluate shoulder alignment (should be level).
        Good: shoulders level
        Bad: shoulders tilted or hunched
        """
        y_diff = abs(left_shoulder.y - right_shoulder.y)
        shoulder_dist = abs(left_shoulder.x - right_shoulder.x)
        
        if shoulder_dist == 0:
            return 0.5
        
        # Ratio of vertical difference to horizontal distance
        tilt_ratio = y_diff / shoulder_dist
        
        # Good alignment when tilt_ratio is small
        alignment_score = max(0, 1 - tilt_ratio * 2)
        
        return alignment_score
    
    def _evaluate_head_position(self, nose, left_shoulder, right_shoulder, left_ear, right_ear):
        """
        Evaluate head position.
        Good: head neutral, aligned with shoulders
        Bad: head tilted, forward/backward lean
        """
        shoulder_x_avg = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_y_avg = (left_shoulder.y + right_shoulder.y) / 2
        
        # Distance from nose to shoulder center
        dist_x = nose.x - shoulder_x_avg
        dist_y = nose.y - shoulder_y_avg
        
        # Head should be mostly above shoulders
        if dist_y > 0.1:  # Head too far forward/down
            forward_lean_penalty = 0.3
        else:
            forward_lean_penalty = 0
        
        # Check head tilt
        ear_y_diff = abs(left_ear.y - right_ear.y)
        ear_x_diff = abs(left_ear.x - right_ear.x)
        
        if ear_x_diff == 0:
            tilt_penalty = 0
        else:
            tilt_penalty = min(0.3, ear_y_diff / ear_x_diff * 0.5)
        
        head_score = max(0, 1 - forward_lean_penalty - tilt_penalty)
        
        return head_score
    
    def _evaluate_gestures(self, left_wrist, right_wrist, left_shoulder, right_shoulder):
        """
        Evaluate hand gestures.
        Good: hands visible, natural gestures, not crossing body excessively
        Bad: hands hidden, no movement, excessive crossing
        """
        shoulder_y_avg = (left_shoulder.y + right_shoulder.y) / 2
        shoulder_x_avg = (left_shoulder.x + right_shoulder.x) / 2
        
        # Check if hands are visible and in reasonable position
        left_wrist_good = (left_wrist.visibility > 0.5 and 
                          left_wrist.y < shoulder_y_avg + 0.3)
        right_wrist_good = (right_wrist.visibility > 0.5 and 
                           right_wrist.y < shoulder_y_avg + 0.3)
        
        visible_hands = sum([left_wrist_good, right_wrist_good])
        visibility_score = visible_hands / 2
        
        # Excessive crossing across body is bad
        left_crossed = left_wrist.x > shoulder_x_avg + 0.2
        right_crossed = right_wrist.x < shoulder_x_avg - 0.2
        crossing_score = 0.7 if not (left_crossed and right_crossed) else 0.3
        
        gesture_score = (visibility_score * 0.6 + crossing_score * 0.4)
        
        return gesture_score
    
    def _compile_analysis(self, processed_frames: int) -> Dict:
        """
        Compile analysis results into a summary.
        
        Args:
            processed_frames: Number of frames processed
        
        Returns:
            Dictionary with analysis results
        """
        if processed_frames == 0:
            return {
                "status": "No body detected",
                "overall_score": 0,
                "assessment": "UNABLE_TO_ANALYZE",
                "details": {}
            }
        
        # Calculate average scores
        avg_posture = np.mean(self.posture_scores) if self.posture_scores else 0
        avg_shoulders = np.mean(self.shoulder_alignment_scores) if self.shoulder_alignment_scores else 0
        avg_head = np.mean(self.head_position_scores) if self.head_position_scores else 0
        avg_gestures = np.mean(self.gesture_scores) if self.gesture_scores else 0
        avg_confidence = np.mean(self.confidence_scores) if self.confidence_scores else 0
        
        # Calculate overall score (weighted average)
        overall_score = (
            avg_posture * 0.35 +
            avg_shoulders * 0.20 +
            avg_head * 0.20 +
            avg_gestures * 0.25
        )
        
        # Determine assessment
        if overall_score >= 0.70:
            assessment = "GOOD"
            interpretation = "Good body language - demonstrates confidence and professionalism"
        elif overall_score >= 0.50:
            assessment = "FAIR"
            interpretation = "Fair body language - room for improvement in posture and gestures"
        else:
            assessment = "BAD"
            interpretation = "Poor body language - needs significant improvement in posture, alignment, or engagement"
        
        return {
            "status": "Analysis Complete",
            "overall_score": round(overall_score, 3),
            "assessment": assessment,
            "interpretation": interpretation,
            "details": {
                "posture_score": round(avg_posture, 3),
                "shoulder_alignment_score": round(avg_shoulders, 3),
                "head_position_score": round(avg_head, 3),
                "gesture_score": round(avg_gestures, 3),
                "detection_confidence": round(avg_confidence, 3),
                "frames_analyzed": processed_frames
            },
            "recommendations": self._generate_recommendations(
                avg_posture, avg_shoulders, avg_head, avg_gestures
            )
        }
    
    def _generate_recommendations(self, posture, shoulders, head, gestures) -> List[str]:
        """
        Generate recommendations based on scores.
        
        Args:
            posture, shoulders, head, gestures: Average scores for each category
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if posture < 0.6:
            recommendations.append("Improve posture - keep your back straight and aligned with hips")
        
        if shoulders < 0.6:
            recommendations.append("Keep shoulders level and relaxed, avoid hunching or tilting")
        
        if head < 0.6:
            recommendations.append("Maintain neutral head position aligned with shoulders, avoid excessive tilting")
        
        if gestures < 0.6:
            recommendations.append("Use more natural hand gestures while keeping them visible and controlled")
        
        if not recommendations:
            recommendations.append("Continue maintaining your excellent body language!")
        
        return recommendations


def analyze_body_language(video_path: str) -> Dict:
    """
    Convenience function to analyze body language in a video.
    
    Args:
        video_path: Path to the MP4 video file
    
    Returns:
        Dictionary with analysis results
    """
    analyzer = BodyLanguageAnalyzer()
    return analyzer.analyze_video(video_path)
