"""
Test script for Body Language Analyzer

Place your MP4 video file in the body_language_module folder and run this script.
"""

import json
from pathlib import Path
from body_language_analyzer import analyze_body_language


def test_body_language():
    """
    Test the body language analyzer with an MP4 file.
    """
    # Specify your video file here
    video_file = "WIN_20260117_05_42_19_Pro.mp4"  # Replace with your actual MP4 filename
    
    video_path = Path(__file__).parent / video_file
    
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        print(f"\nPlease place your MP4 file in the body_language_module folder")
        print(f"and update the video_file variable in this script.\n")
        print("Expected structure:")
        print("body_language_module/")
        print("  ├── body_language_analyzer.py")
        print("  ├── test.py")
        print("  └── your_video.mp4")
        return
    
    print("=" * 60)
    print("Body Language Analysis Test")
    print("=" * 60)
    print(f"\nAnalyzing: {video_file}\n")
    
    try:
        # Run analysis
        results = analyze_body_language(str(video_path))
        
        # Display results
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"\nStatus: {results['status']}")
        print(f"Overall Score: {results['overall_score']} (0-1 scale)")
        print(f"Assessment: {results['assessment']}")
        print(f"\nInterpretation:\n  {results['interpretation']}")
        
        # Detailed scores
        print("\n" + "-" * 60)
        print("DETAILED SCORES")
        print("-" * 60)
        details = results['details']
        print(f"Posture Score:            {details['posture_score']}")
        print(f"Shoulder Alignment Score: {details['shoulder_alignment_score']}")
        print(f"Head Position Score:      {details['head_position_score']}")
        print(f"Gesture Score:            {details['gesture_score']}")
        print(f"Detection Confidence:     {details['detection_confidence']}")
        print(f"Frames Analyzed:          {details['frames_analyzed']}")
        
        # Recommendations
        print("\n" + "-" * 60)
        print("RECOMMENDATIONS")
        print("-" * 60)
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 60)
        
        # Optional: Save results to JSON
        output_file = video_path.parent / f"{video_path.stem}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_body_language()
