"""
ElevenLabs Text-to-Speech Generator

This script uses the ElevenLabs API to convert text into natural-sounding speech.
It supports multiple voices and provides options for saving audio files.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment variables from .env file
load_dotenv()


class TextToSpeech:
    """
    A class to handle text-to-speech conversion using ElevenLabs API.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the TextToSpeech client.
        
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
        
        # Set default voice ID from environment or use Rachel as default
        self.default_voice_id = os.getenv("DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        
        # Set output directory
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_speech(
        self,
        text: str,
        voice_id: str = None,
        output_filename: str = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> str:
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text (str): The text to convert to speech
            voice_id (str, optional): Voice ID to use. Defaults to DEFAULT_VOICE_ID
            output_filename (str, optional): Name of output file. Auto-generated if not provided
            stability (float): Voice stability (0.0 to 1.0). Lower = more variable/expressive
            similarity_boost (float): Voice similarity (0.0 to 1.0). Higher = closer to original voice
            style (float): Style exaggeration (0.0 to 1.0). Higher = more exaggerated
            use_speaker_boost (bool): Enable speaker boost for better quality
        
        Returns:
            str: Path to the generated audio file
        """
        # Use default voice if none specified
        voice_id = voice_id or self.default_voice_id
        
        # Generate output filename if not provided
        if not output_filename:
            # Create a safe filename from the first 50 characters of text
            safe_text = "".join(c for c in text[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_text = safe_text.replace(' ', '_')
            output_filename = f"{safe_text}.mp3"
        
        # Ensure the filename has .mp3 extension
        if not output_filename.endswith('.mp3'):
            output_filename += '.mp3'
        
        output_path = self.output_dir / output_filename
        
        print(f"Generating speech for: '{text[:50]}...'")
        print(f"Using voice ID: {voice_id}")
        
        try:
            # Generate speech using the ElevenLabs API
            response = self.client.text_to_speech.convert(
                voice_id=voice_id,
                optimize_streaming_latency="0",
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2",  # Use the latest multilingual model
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    use_speaker_boost=use_speaker_boost,
                ),
            )
            
            # Save the audio file
            with open(output_path, "wb") as f:
                for chunk in response:
                    if chunk:
                        f.write(chunk)
            
            print(f"✓ Audio saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"✗ Error generating speech: {str(e)}")
            raise
    
    def list_available_voices(self):
        """
        List all available voices from your ElevenLabs account.
        
        Returns:
            list: List of available voices with their IDs and names
        """
        try:
            voices = self.client.voices.get_all()
            print("\n=== Available Voices ===")
            for voice in voices.voices:
                print(f"- {voice.name}: {voice.voice_id}")
            return voices.voices
        except Exception as e:
            print(f"✗ Error fetching voices: {str(e)}")
            raise


def main():
    """
    Main function demonstrating usage of the TextToSpeech class.
    """
    try:
        # Initialize the TTS client
        tts = TextToSpeech()
        
        # Example 1: Simple text-to-speech conversion
        print("\n=== Example 1: Basic Usage ===")
        text1 = "Hello! This is a demonstration of the ElevenLabs text-to-speech API."
        tts.generate_speech(text1, output_filename="example1.mp3")
        
        # Example 2: Custom voice settings for more expressive speech
        print("\n=== Example 2: Expressive Speech ===")
        text2 = "Wow! This is amazing! I can't believe how realistic this sounds!"
        tts.generate_speech(
            text2,
            output_filename="example2_expressive.mp3",
            stability=0.3,  # Lower stability for more variation
            style=0.5       # Add some style exaggeration
        )
        
        # Example 3: More stable, professional-sounding speech
        print("\n=== Example 3: Professional Speech ===")
        text3 = "Welcome to our presentation. Today we will discuss the latest developments in artificial intelligence."
        tts.generate_speech(
            text3,
            output_filename="example3_professional.mp3",
            stability=0.8,  # Higher stability for consistency
            style=0.0       # No style exaggeration
        )
        
        # List available voices
        print("\n=== Listing Available Voices ===")
        tts.list_available_voices()
        
        print("\n✓ All examples completed successfully!")
        print(f"Check the '{tts.output_dir}' folder for generated audio files.")
        
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
