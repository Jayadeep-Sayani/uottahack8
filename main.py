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

from question_generator import InterviewQuestionGenerator
from text_to_speech import TextToSpeech


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
