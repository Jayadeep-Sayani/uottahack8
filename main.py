"""
Main module that generates interview questions using Gemini and converts them to voice using ElevenLabs TTS.
"""

import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "gemini_question_gen"))
sys.path.insert(0, str(Path(__file__).parent / "eleven_labs_tts"))
sys.path.insert(0, str(Path(__file__).parent / "body_language_module"))
sys.path.insert(0, str(Path(__file__).parent / "confidence_analysis_module"))
sys.path.insert(0, str(Path(__file__).parent / "speech_modulation"))

from gemini_question_gen.question_generator import InterviewQuestionGenerator
from eleven_labs_tts.text_to_speech import TextToSpeech
from body_language_module.body_language_analyzer import analyze_body_language
from body_language_module import analyze_eye_contact
from confidence_analysis_module import analyze_speech
from speech_modulation import SpeechModulationAnalyzer
import json


class InterviewPreparationSystem:
    """
    Integrated system to generate interview questions and convert them to voice recordings.
    """
    
    def __init__(self):
        """Initialize the interview preparation system."""
        self.question_generator = InterviewQuestionGenerator()
        self.tts_generator = TextToSpeech()
        self.output_dir = Path(__file__).parent / "interview_output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Create or clear user_recordings directory
        self.user_recordings_dir = Path(__file__).parent / "user_recordings"
        if self.user_recordings_dir.exists():
            shutil.rmtree(self.user_recordings_dir)
        self.user_recordings_dir.mkdir(exist_ok=True)
    
    def generate_and_convert_questions(self, company_name: str, job_description: str):
        """
        Generate interview questions and convert each to voice.
        
        Args:
            company_name: Name of the company
            job_description: Description of the job position
        """
        print("=" * 60)
        print("Interview Preparation System")
        print("=" * 60)
        print(f"\nCompany: {company_name}")
        print(f"Position: {job_description[:50]}...")
        print("\nGenerating questions...")
        
        # Generate questions using Gemini
        questions = self.question_generator.generate_questions(company_name, job_description)
        
        total_questions = (
            len(questions["introduction"]) +
            len(questions["regular"]) +
            len(questions["situational"])
        )
        print(f"✓ Generated {total_questions} questions\n")
        
        question_num = 1
        audio_files = []
        
        print("=" * 60)
        print("Generating Voice Recordings")
        print("=" * 60 + "\n")
        
        # Process introduction question first
        if questions["introduction"]:
            question_text = questions["introduction"][0]
            audio_file = self._generate_voice_for_question(
                question_num, "Introduction", question_text
            )
            audio_files.append(audio_file)
            question_num += 1
        
        # Process regular questions
        for regular_q in questions["regular"]:
            audio_file = self._generate_voice_for_question(
                question_num, "Regular", regular_q
            )
            audio_files.append(audio_file)
            question_num += 1
        
        # Process situational questions last
        for situational_q in questions["situational"]:
            audio_file = self._generate_voice_for_question(
                question_num, "Situational", situational_q
            )
            audio_files.append(audio_file)
            question_num += 1
        
        print("=" * 60)
        print("✓ All voice recordings completed successfully!")
        print("=" * 60)
        print(f"\nAudio files saved to: {self.output_dir}")
        print(f"Total files generated: {len(audio_files)}")
        
        return audio_files
    
    def _generate_voice_for_question(self, question_num: int, question_type: str, question_text: str) -> str:
        """
        Generate a voice recording for a single question.
        
        Args:
            question_num: Question number
            question_type: Type of question (Introduction, Regular, Situational)
            question_text: The question text
        
        Returns:
            Path to the generated audio file
        """
        print(f"Question {question_num} ({question_type}):")
        print(f"{question_text}\n")
        
        # Create filename
        safe_type = question_type.replace(" ", "_")
        filename = f"Question_{question_num}_{safe_type}.mp3"
        output_path = self.output_dir / filename
        
        # Generate speech
        self.tts_generator.output_dir = self.output_dir
        self.tts_generator.generate_speech(
            question_text,
            output_filename=filename,
            stability=0.7,
            similarity_boost=0.75
        )
        print()
        
        return str(output_path)


def analyze_interview_performance(video_path: str, audio_path: str = None):
    """
    Analyze interview performance using all analysis modules.
    Creates JSON files for body language, eye contact, speech confidence, and speech modulation.
    
    Args:
        video_path: Path to the video file (MP4) for body language and eye contact analysis
        audio_path: Optional path to audio file. If None, will try to extract from video or use video path
    
    Returns:
        Dictionary with paths to all generated JSON files
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Use video path for audio if audio_path not provided
    if audio_path is None:
        audio_path = video_path
    else:
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    print("=" * 60)
    print("Interview Performance Analysis")
    print("=" * 60)
    print(f"\nVideo: {video_path.name}")
    if audio_path != video_path:
        print(f"Audio: {audio_path.name}")
    print()
    
    output_dir = video_path.parent
    base_name = video_path.stem
    
    results = {}
    
    # 1. Body Language Analysis
    print("Analyzing body language...")
    try:
        body_language_results = analyze_body_language(str(video_path))
        body_language_json = output_dir / f"{base_name}_body_language_analysis.json"
        with open(body_language_json, 'w') as f:
            json.dump(body_language_results, f, indent=2)
        results["body_language"] = str(body_language_json)
        print(f"✓ Body language analysis saved to: {body_language_json.name}")
    except Exception as e:
        print(f"✗ Body language analysis failed: {e}")
        results["body_language"] = None
    
    print()
    
    # 2. Eye Contact Analysis
    print("Analyzing eye contact...")
    try:
        eye_contact_results = analyze_eye_contact(str(video_path))
        eye_contact_json = output_dir / f"{base_name}_eye_contact_analysis.json"
        with open(eye_contact_json, 'w') as f:
            json.dump(eye_contact_results, f, indent=2)
        results["eye_contact"] = str(eye_contact_json)
        print(f"✓ Eye contact analysis saved to: {eye_contact_json.name}")
    except Exception as e:
        print(f"✗ Eye contact analysis failed: {e}")
        results["eye_contact"] = None
    
    print()
    
    # 3. Speech Confidence Analysis
    print("Analyzing speech confidence...")
    try:
        speech_results = analyze_speech(str(audio_path))
        speech_json = output_dir / f"{base_name}_speech_confidence_analysis.json"
        with open(speech_json, 'w') as f:
            json.dump(speech_results, f, indent=2)
        results["speech_confidence"] = str(speech_json)
        print(f"✓ Speech confidence analysis saved to: {speech_json.name}")
    except Exception as e:
        print(f"✗ Speech confidence analysis failed: {e}")
        results["speech_confidence"] = None
    
    print()
    
    # 4. Speech Modulation Analysis
    print("Analyzing speech modulation...")
    try:
        modulation_analyzer = SpeechModulationAnalyzer()
        # Temporarily set output_dir to save in same location as other analyses
        original_output_dir = modulation_analyzer.output_dir
        modulation_analyzer.output_dir = output_dir
        modulation_results = modulation_analyzer.analyze(str(video_path))
        # The analyze method saves the file, so we just need to get the path
        modulation_json = output_dir / f"{base_name}_modulation_analysis.json"
        # Restore original output_dir
        modulation_analyzer.output_dir = original_output_dir
        results["speech_modulation"] = str(modulation_json)
        print(f"✓ Speech modulation analysis saved to: {modulation_json.name}")
    except Exception as e:
        print(f"✗ Speech modulation analysis failed: {e}")
        results["speech_modulation"] = None
    
    print()
    print("=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\nGenerated JSON files:")
    for analysis_type, file_path in results.items():
        if file_path:
            print(f"  - {analysis_type}: {Path(file_path).name}")
        else:
            print(f"  - {analysis_type}: Failed")
    
    return results


def main():
    """
    Main function to run the interview preparation system.
    """
    try:
        # Hardcoded company name and job description
        company_name = "Google"
        job_description = "Senior Software Engineer - Backend with 5+ years experience in Python and cloud infrastructure"
        
        # Create the system
        system = InterviewPreparationSystem()
        
        # Generate and convert questions
        system.generate_and_convert_questions(company_name, job_description)
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("1. GEMINI_API_KEY environment variable is set in .env")
        print("2. ELEVENLABS_API_KEY environment variable is set in .env")
        print("3. Both API keys are valid")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
