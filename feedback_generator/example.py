"""
Example script demonstrating how to use the InterviewFeedbackGenerator.
"""

from feedback_generator import InterviewFeedbackGenerator, generate_interview_feedback
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def example_basic_usage():
    """Example of basic usage with the class."""
    print("=" * 60)
    print("Example 1: Basic Usage with InterviewFeedbackGenerator")
    print("=" * 60)
    
    # Initialize the generator
    generator = InterviewFeedbackGenerator()
    
    # Example inputs
    company_name = "Tech Corp"
    job_description = "Senior Software Engineer - Backend Development"
    question_text = "Tell me about yourself and why you're interested in this role."
    
    # Paths to analysis JSON files (update these paths to match your files)
    base_path = "WIN_20260117_06_08_56_Pro"
    speech_confidence_json_path = f"{base_path}_speech_confidence_analysis.json"
    body_language_json_path = f"{base_path}_body_language_analysis.json"
    eye_contact_json_path = f"{base_path}_eye_contact_analysis.json"
    modulation_json_path = f"{base_path}_modulation_analysis.json"
    
    # Check if files exist
    json_files = [
        speech_confidence_json_path,
        body_language_json_path,
        eye_contact_json_path,
        modulation_json_path
    ]
    
    missing_files = [f for f in json_files if not os.path.exists(f)]
    if missing_files:
        print(f"\nWarning: The following JSON files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nPlease update the file paths in this script to match your actual files.")
        return
    
    # Generate feedback
    print(f"\nGenerating feedback for question:\n{question_text}\n")
    print("Analyzing data from:")
    for f in json_files:
        print(f"  - {f}")
    print()
    
    feedback = generator.generate_feedback(
        company_name=company_name,
        job_description=job_description,
        question_text=question_text,
        speech_confidence_json_path=speech_confidence_json_path,
        body_language_json_path=body_language_json_path,
        eye_contact_json_path=eye_contact_json_path,
        modulation_json_path=modulation_json_path
    )
    
    # Display feedback
    print("Generated Feedback:")
    print("-" * 60)
    for i, point in enumerate(feedback["feedback"], 1):
        print(f"{i}. {point}")
    
    # Save feedback to file
    output_path = f"{base_path}_feedback.json"
    generator.save_feedback(feedback, output_path)
    print(f"\nFeedback saved to: {output_path}")


def example_convenience_function():
    """Example using the convenience function."""
    print("\n" + "=" * 60)
    print("Example 2: Using the Convenience Function")
    print("=" * 60)
    
    base_path = "WIN_20260117_06_08_56_Pro"
    
    # Check if files exist
    json_files = [
        f"{base_path}_speech_confidence_analysis.json",
        f"{base_path}_body_language_analysis.json",
        f"{base_path}_eye_contact_analysis.json",
        f"{base_path}_modulation_analysis.json"
    ]
    
    missing_files = [f for f in json_files if not os.path.exists(f)]
    if missing_files:
        print(f"\nWarning: The following JSON files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        return
    
    # Generate feedback using convenience function
    feedback = generate_interview_feedback(
        company_name="Google",
        job_description="Software Engineer - Full Stack",
        question_text="Describe a challenging project you worked on.",
        speech_confidence_json_path=f"{base_path}_speech_confidence_analysis.json",
        body_language_json_path=f"{base_path}_body_language_analysis.json",
        eye_contact_json_path=f"{base_path}_eye_contact_analysis.json",
        modulation_json_path=f"{base_path}_modulation_analysis.json",
        output_json_path=f"{base_path}_feedback_convenience.json"
    )
    
    print("\nGenerated Feedback:")
    print("-" * 60)
    for i, point in enumerate(feedback["feedback"], 1):
        print(f"{i}. {point}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set your Gemini API key:")
        print("  Windows (PowerShell): $env:GEMINI_API_KEY='your-api-key'")
        print("  Windows (CMD): set GEMINI_API_KEY=your-api-key")
        print("  macOS/Linux: export GEMINI_API_KEY='your-api-key'")
        exit(1)
    
    # Run examples
    try:
        example_basic_usage()
        example_convenience_function()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
