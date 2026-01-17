"""
ElevenLabs Speech-to-Text Converter

This script uses the ElevenLabs Scribe API to convert audio/video files to text.
It supports MP4, MP3, WAV, and other audio formats with real-time transcription.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import subprocess
import json
import requests  # For direct API calls

# Load environment variables from .env file
load_dotenv()


class SpeechToText:
    """
    A class to handle speech-to-text conversion using ElevenLabs Scribe API.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the SpeechToText client.
        
        Args:
            api_key (str, optional): ElevenLabs API key. If not provided, 
                                     will be loaded from environment variable.
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "ElevenLabs API key not found. Please set ELEVENLABS_API_KEY "
                "in your .env file or pass it to the constructor."
            )
        
        # Initialize the ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Set output directory for transcripts
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_audio_from_video(self, video_path: str, audio_path: str = None) -> str:
        """
        Extract audio from video file using ffmpeg.
        
        Args:
            video_path (str): Path to the video file
            audio_path (str, optional): Path for the extracted audio file
        
        Returns:
            str: Path to the extracted audio file
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Generate audio path if not provided
        if not audio_path:
            audio_path = self.output_dir / f"{video_path.stem}_audio.mp3"
        
        audio_path = Path(audio_path)
        
        print(f"Extracting audio from: {video_path.name}")
        
        try:
            # Use ffmpeg to extract audio
            command = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'libmp3lame',  # MP3 codec
                '-q:a', '2',  # High quality
                '-y',  # Overwrite output file
                str(audio_path)
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"✓ Audio extracted to: {audio_path}")
            return str(audio_path)
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Error extracting audio: {e.stderr}")
            raise
        except FileNotFoundError:
            print("✗ ffmpeg not found. Please install ffmpeg:")
            print("  Windows: Download from https://ffmpeg.org/download.html")
            print("  Or use: winget install ffmpeg")
            raise
    
    def transcribe_file(
        self,
        file_path: str,
        language: str = "en",
        include_timestamps: bool = True,
        output_format: str = "txt"
    ) -> dict:
        """
        Transcribe an audio or video file to text.
        
        Args:
            file_path (str): Path to the audio/video file
            language (str): Language code (e.g., 'en', 'es', 'fr')
            include_timestamps (bool): Include word-level timestamps
            output_format (str): Output format - 'txt', 'json', or 'srt'
        
        Returns:
            dict: Transcription result with text and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract audio if it's a video file
        if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            print(f"Detected video file: {file_path.name}")
            audio_path = self.extract_audio_from_video(str(file_path))
            file_to_transcribe = audio_path
        else:
            file_to_transcribe = str(file_path)
        
        print(f"\nTranscribing: {Path(file_to_transcribe).name}")
        print(f"Language: {language}")
        print(f"Timestamps: {'Yes' if include_timestamps else 'No'}")
        
        try:
            # Open and read the audio file
            with open(file_to_transcribe, 'rb') as audio_file:
                # Use ElevenLabs Scribe API via direct REST API call
                # The SDK doesn't support speech-to-text yet, so we use requests
                import requests
                
                url = "https://api.elevenlabs.io/v1/speech-to-text"
                
                headers = {
                    "xi-api-key": self.api_key
                }
                
                files = {
                    "file": audio_file
                }
                
                data = {
                    "model_id": "scribe_v2",
                    "language": language
                }
                
                print(f"Sending request to ElevenLabs API...")
                response = requests.post(url, headers=headers, files=files, data=data)
                
                if response.status_code == 200:
                    transcription_data = response.json()
                    transcript_text = transcription_data.get('text', '')
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    raise Exception(error_msg)
            
            # Extract the transcription text
            result = {
                'text': transcript_text,
                'file': str(file_path),
                'language': language,
                'timestamps_included': include_timestamps
            }
            
            print(f"\n✓ Transcription completed!")
            print(f"Length: {len(transcript_text)} characters")
            
            # Save the transcription
            self._save_transcription(result, file_path.stem, output_format)
            
            return result
            
        except Exception as e:
            print(f"\n✗ Error during transcription: {str(e)}")
            raise
    
    def _save_transcription(self, result: dict, base_name: str, output_format: str):
        """
        Save transcription to file in the specified format.
        
        Args:
            result (dict): Transcription result
            base_name (str): Base name for the output file
            output_format (str): Output format - 'txt', 'json', or 'srt'
        """
        if output_format == 'txt':
            output_path = self.output_dir / f"{base_name}_transcript.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
        
        elif output_format == 'json':
            output_path = self.output_dir / f"{base_name}_transcript.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        elif output_format == 'srt':
            # For SRT format, we'd need timestamps which may not be available
            # in the basic API response. Fallback to TXT for now.
            output_path = self.output_dir / f"{base_name}_transcript.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            print("Note: SRT format requires timestamps. Saved as TXT instead.")
        
        print(f"✓ Transcript saved to: {output_path}")


def main():
    """
    Main function demonstrating usage of the SpeechToText class.
    """
    try:
        # Initialize the STT client
        stt = SpeechToText()
        
        print("=== ElevenLabs Speech-to-Text Demo ===\n")
        
        # Example: Transcribe a file
        # Replace with your actual file path
        file_path = input("Enter the path to your audio/video file (or press Enter to skip): ").strip()
        
        if file_path and file_path != "":
            # Remove quotes if user copied path with quotes
            file_path = file_path.strip('"').strip("'")
            
            if Path(file_path).exists():
                # Transcribe the file
                result = stt.transcribe_file(
                    file_path=file_path,
                    language="en",
                    include_timestamps=True,
                    output_format="txt"
                )
                
                # Display the transcription
                print("\n" + "="*50)
                print("TRANSCRIPTION:")
                print("="*50)
                print(result['text'])
                print("="*50)
                
                print(f"\n✓ Transcription saved to the '{stt.output_dir}' folder")
            else:
                print(f"✗ File not found: {file_path}")
        else:
            print("\nNo file provided. Here's how to use the script:")
            print("\nExample usage:")
            print("  python speech_to_text.py")
            print("\nOr in your own code:")
            print("  from speech_to_text import SpeechToText")
            print("  stt = SpeechToText()")
            print("  result = stt.transcribe_file('path/to/video.mp4')")
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease follow these steps:")
        print("1. Get your API key from: https://elevenlabs.io/app/settings/api-keys")
        print("2. Open the .env file and replace 'your_api_key_here' with your actual API key")
        print("3. Run this script again")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")


if __name__ == "__main__":
    main()
