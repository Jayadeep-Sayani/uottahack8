"""
Test script for Eye Contact Analyzer

Place your MP4 video file in the body_language_module folder and run this script.
"""

import json
from pathlib import Path
from eye_contact_analyzer import analyze_eye_contact


def test_eye_contact():
    """
    Test the eye contact analyzer with an MP4 file.
    """
    # Specify your video file here
    video_file = "WIN_20260117_06_08_56_Pro.mp4"  # Replace with your actual MP4 filename
    
    video_path = Path(__file__).parent / video_file
    
    if not video_path.exists():
        print(f"Error: Video file not found at {video_path}")
        print(f"\nPlease place your MP4 file in the body_language_module folder")
        print(f"and update the video_file variable in this script.\n")
        print("Expected structure:")
        print("body_language_module/")
        print("  ├── body_language_analyzer.py")
        print("  ├── eye_contact_analyzer.py")
        print("  ├── test_eye_contact.py")
        print("  └── your_video.mp4")
        return
    
    print("=" * 60)
    print("Eye Contact Analysis Test")
    print("=" * 60)
    print(f"\nAnalyzing: {video_file}\n")
    
    try:
        # Run analysis
        results = analyze_eye_contact(str(video_path))
        
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
        print(f"Eye Contact Score:   {details['eye_contact_score']}")
        print(f"Eye Opening Score:   {details['eye_opening_score']}")
        print(f"Frames Analyzed:     {details['frames_analyzed']}")
        
        # Recommendations
        print("\n" + "-" * 60)
        print("RECOMMENDATIONS")
        print("-" * 60)
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 60)
        
        # Save results to JSON
        output_file = video_path.parent / f"{video_path.stem}_eye_contact_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_eye_contact()
