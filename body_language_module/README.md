# Body Language Analyzer

A Python module that analyzes video files to assess body language quality using pose estimation.

## Features

- **Pose Detection**: Uses MediaPipe to detect body landmarks from video
- **Multi-aspect Analysis**: Evaluates:
  - Posture quality (spine straightness, slouching)
  - Shoulder alignment (level shoulders)
  - Head position (tilting, forward lean)
  - Hand gestures (visibility, natural positioning)
- **Comprehensive Scoring**: Provides overall score (0-1) and categorized scores
- **Assessment Categories**: GOOD, FAIR, or BAD
- **Actionable Recommendations**: Specific feedback for improvement

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from body_language_analyzer import BodyLanguageAnalyzer

# Initialize analyzer
analyzer = BodyLanguageAnalyzer()

# Analyze video
results = analyzer.analyze_video("video.mp4")

# Print results
print(f"Assessment: {results['assessment']}")
print(f"Overall Score: {results['overall_score']}")
print(f"Interpretation: {results['interpretation']}")
print(f"Recommendations: {results['recommendations']}")
```

### Using Convenience Function

```python
from body_language_analyzer import analyze_body_language

results = analyze_body_language("video.mp4")
```

## Output Format

The analyzer returns a dictionary with the following structure:

```python
{
    "status": "Analysis Complete",
    "overall_score": 0.742,  # 0-1 score
    "assessment": "GOOD",     # GOOD, FAIR, or BAD
    "interpretation": "Good body language - demonstrates confidence and professionalism",
    "details": {
        "posture_score": 0.75,
        "shoulder_alignment_score": 0.72,
        "head_position_score": 0.68,
        "gesture_score": 0.80,
        "detection_confidence": 0.85,
        "frames_analyzed": 120
    },
    "recommendations": [
        "List of actionable recommendations for improvement"
    ]
}
```

## Scoring Breakdown

- **Posture Score** (35% weight): Measures spine alignment and slouching
- **Shoulder Alignment** (20% weight): Evaluates shoulder levelness
- **Head Position** (20% weight): Checks for head tilt and forward lean
- **Gesture Score** (25% weight): Assesses hand visibility and positioning

## Assessment Levels

- **GOOD** (≥0.70): Demonstrates confidence and professionalism
- **FAIR** (0.50-0.69): Room for improvement in posture and gestures
- **BAD** (<0.50): Needs significant improvement

## Requirements

- Python 3.7+
- opencv-python - Video processing
- mediapipe - Pose estimation
- numpy - Numerical operations

## Limitations

- Requires clear visibility of the person's body
- Works best in well-lit environments
- Analyzes every 5th frame for performance
- Detection confidence depends on video quality and camera angle
