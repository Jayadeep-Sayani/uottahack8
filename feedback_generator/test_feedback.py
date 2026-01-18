"""
Test script for Interview Feedback Generator

This test script uses existing analysis JSON files to generate feedback.
It expects the 4 analysis JSON files to be available (speech confidence, 
body language, eye contact, and modulation analysis).
"""

import json
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from feedback_generator import InterviewFeedbackGenerator, generate_interview_feedback


def find_json_files(base_name: str, search_dirs: list = None) -> dict:
    """
    Find the 4 required JSON analysis files in common locations.
    
    Args:
        base_name: Base name of the files (e.g., "WIN_20260117_06_08_56_Pro")
        search_dirs: List of directories to search in (defaults to common locations)
    
    Returns:
        Dictionary with file paths or None if not found
    """
    if search_dirs is None:
        search_dirs = [
            Path(__file__).parent.parent,  # Root directory
            Path(__file__).parent.parent / "confidence_analysis_module",
            Path(__file__).parent.parent / "speech_modulation" / "output",
            Path(__file__).parent.parent / "body_language_module",
        ]
    
    file_types = {
        "speech_confidence": f"{base_name}_speech_confidence_analysis.json",
        "body_language": f"{base_name}_body_language_analysis.json",
        "eye_contact": f"{base_name}_eye_contact_analysis.json",
        "modulation": f"{base_name}_modulation_analysis.json"
    }
    
    found_files = {}
    
    for file_type, filename in file_types.items():
        found = False
        for search_dir in search_dirs:
            file_path = search_dir / filename
            if file_path.exists():
                found_files[file_type] = str(file_path)
                found = True
                break
        
        if not found:
            found_files[file_type] = None
    
    return found_files


def test_feedback_generator():
    """
    Test the feedback generator with existing analysis JSON files.
    """
    print("=" * 70)
    print("Interview Feedback Generator Test")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("\n✗ Error: GEMINI_API_KEY environment variable not set.")
        print("\nPlease set your Gemini API key:")
        print("  Windows (PowerShell): $env:GEMINI_API_KEY='your-api-key'")
        print("  Windows (CMD): set GEMINI_API_KEY=your-api-key")
        print("  macOS/Linux: export GEMINI_API_KEY='your-api-key'")
        print("\n" + "=" * 70)
        return
    
    # Try to find existing analysis files
    base_name = "WIN_20260117_06_08_56_Pro"
    json_files = find_json_files(base_name)
    
    # Check which files are missing
    missing_files = {k: v for k, v in json_files.items() if v is None}
    
    if missing_files:
        print(f"\n⚠ Warning: Some analysis JSON files are missing for '{base_name}':")
        for file_type in missing_files.keys():
            expected_name = f"{base_name}_{file_type.replace('_', '_')}_analysis.json"
            print(f"  - {expected_name}")
        
        print(f"\nSearched in the following locations:")
        search_dirs = [
            Path(__file__).parent.parent,
            Path(__file__).parent.parent / "confidence_analysis_module",
            Path(__file__).parent.parent / "speech_modulation" / "output",
        ]
        for search_dir in search_dirs:
            print(f"  - {search_dir}")
        
        print(f"\nPlease ensure all 4 analysis JSON files exist, or update the")
        print(f"base_name variable in this script to match your files.")
        print("\nRequired files:")
        print(f"  1. {base_name}_speech_confidence_analysis.json")
        print(f"  2. {base_name}_body_language_analysis.json")
        print(f"  3. {base_name}_eye_contact_analysis.json")
        print(f"  4. {base_name}_modulation_analysis.json")
        print("\n" + "=" * 70)
        return
    
    print(f"\n✓ Found all 4 required analysis JSON files:")
    for file_type, file_path in json_files.items():
        print(f"  - {file_type}: {Path(file_path).name}")
    
    # Example inputs
    company_name = "Tech Corp"
    job_description = "Senior Software Engineer - Backend Development with focus on scalable systems and API design"
    question_text = "Tell me about yourself and why you're interested in this role at our company."
    
    print(f"\n" + "=" * 70)
    print("INPUT PARAMETERS")
    print("=" * 70)
    print(f"\nCompany: {company_name}")
    print(f"\nJob Description: {job_description}")
    print(f"\nQuestion: {question_text}")
    
    try:
        print(f"\n" + "=" * 70)
        print("GENERATING FEEDBACK...")
        print("=" * 70)
        print("\nThis may take a few moments as it uses Gemini API...\n")
        
        # Initialize generator
        generator = InterviewFeedbackGenerator()
        
        # Generate feedback
        feedback = generator.generate_feedback(
            company_name=company_name,
            job_description=job_description,
            question_text=question_text,
            speech_confidence_json_path=json_files["speech_confidence"],
            body_language_json_path=json_files["body_language"],
            eye_contact_json_path=json_files["eye_contact"],
            modulation_json_path=json_files["modulation"]
        )
        
        # Display results
        print("=" * 70)
        print("GENERATED FEEDBACK")
        print("=" * 70)
        
        if "feedback" in feedback and isinstance(feedback["feedback"], list):
            for i, point in enumerate(feedback["feedback"], 1):
                print(f"\n{i}. {point}")
        else:
            print("\n⚠ Unexpected feedback format:")
            print(json.dumps(feedback, indent=2))
        
        # Save feedback to file
        output_path = Path(__file__).parent.parent / f"{base_name}_feedback.json"
        generator.save_feedback(feedback, str(output_path))
        print(f"\n" + "=" * 70)
        print(f"✓ Feedback saved to: {output_path.name}")
        print("=" * 70)
        
        # Also display the JSON structure
        print(f"\nJSON Structure:")
        print(json.dumps(feedback, indent=2))
        
    except Exception as e:
        print(f"\n✗ Error during feedback generation: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 70)


def test_convenience_function():
    """
    Test the convenience function for generating feedback.
    """
    print("\n\n" + "=" * 70)
    print("Testing Convenience Function")
    print("=" * 70)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("\n✗ Skipping: GEMINI_API_KEY not set")
        return
    
    # Find JSON files
    base_name = "WIN_20260117_06_08_56_Pro"
    json_files = find_json_files(base_name)
    
    # Check if all files exist
    if any(v is None for v in json_files.values()):
        print(f"\n⚠ Skipping: Some JSON files are missing")
        return
    
    try:
        print("\nGenerating feedback using convenience function...\n")
        
        feedback = generate_interview_feedback(
            company_name="Google",
            job_description="Software Engineer - Full Stack Development",
            question_text="Describe a challenging technical project you worked on and how you solved it.",
            speech_confidence_json_path=json_files["speech_confidence"],
            body_language_json_path=json_files["body_language"],
            eye_contact_json_path=json_files["eye_contact"],
            modulation_json_path=json_files["modulation"],
            output_json_path=str(Path(__file__).parent.parent / f"{base_name}_feedback_convenience.json")
        )
        
        print("✓ Feedback generated successfully!")
        print(f"\nFeedback points ({len(feedback.get('feedback', []))}):")
        for i, point in enumerate(feedback.get("feedback", []), 1):
            print(f"  {i}. {point}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_json_loading():
    """
    Test that we can load all the JSON files correctly.
    """
    print("\n\n" + "=" * 70)
    print("Testing JSON File Loading")
    print("=" * 70)
    
    base_name = "WIN_20260117_06_08_56_Pro"
    json_files = find_json_files(base_name)
    
    print(f"\nChecking JSON file structure...\n")
    
    for file_type, file_path in json_files.items():
        if file_path is None:
            print(f"✗ {file_type}: File not found")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ {file_type}: Valid JSON loaded")
            print(f"  Keys: {list(data.keys())}")
        except Exception as e:
            print(f"✗ {file_type}: Error loading JSON - {e}")


if __name__ == "__main__":
    # Run all tests
    test_json_loading()
    test_feedback_generator()
    test_convenience_function()
    
    print("\n\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)
