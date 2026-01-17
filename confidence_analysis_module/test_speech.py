"""
Test script for Speech Analyzer

Place your MP4 video file (or audio file) in the speech_analysis_module folder and run this script.
The script will extract audio from MP4 files if needed.
"""

import json
import subprocess
import shutil
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from speech_analysis_module.speech_analyzer import analyze_speech


def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is available in the system PATH."""
    return shutil.which("ffmpeg") is not None


def extract_audio_from_mp4_ffmpeg(video_path: Path) -> Path:
    """
    Extract audio from MP4 using ffmpeg directly via subprocess.
    
    Args:
        video_path: Path to MP4 video file
    
    Returns:
        Path to extracted WAV audio file
    """
    audio_path = video_path.with_suffix(".wav")
    
    # Use ffmpeg command line to extract audio
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit audio codec
        "-ar", "44100",  # Sample rate
        "-ac", "2",  # Stereo channels
        "-y",  # Overwrite output file if it exists
        str(audio_path)
    ]
    
    try:
        # Run ffmpeg, suppress output
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return audio_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg extraction failed: {e.stderr}")
    except FileNotFoundError:
        raise Exception("FFmpeg not found in system PATH")


def extract_audio_from_mp4(video_path: Path) -> Path:
    """
    Extract audio from MP4 file and save as WAV.
    Tries multiple methods in order: direct ffmpeg, moviepy, pydub.
    
    Args:
        video_path: Path to MP4 video file
    
    Returns:
        Path to extracted WAV audio file
    """
    print("Extracting audio from MP4...")
    
    # Method 1: Try direct ffmpeg (fastest and most reliable)
    if check_ffmpeg_available():
        try:
            audio_path = extract_audio_from_mp4_ffmpeg(video_path)
            print(f"✓ Audio extracted to: {audio_path.name} (using ffmpeg)")
            return audio_path
        except Exception as e:
            print(f"Warning: Direct ffmpeg failed: {e}")
            print("Trying alternative methods...")
    
    # Method 2: Try using moviepy
    try:
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(str(video_path))
        audio_path = video_path.with_suffix(".wav")
        video.audio.write_audiofile(str(audio_path), logger=None)
        video.close()
        print(f"✓ Audio extracted to: {audio_path.name} (using moviepy)")
        return audio_path
    except ImportError:
        pass  # Continue to next method
    except Exception as e:
        print(f"Warning: moviepy extraction failed: {e}")
    
    # Method 3: Try using pydub
    try:
        from pydub import AudioSegment
        print("Using pydub for audio extraction...")
        audio = AudioSegment.from_file(str(video_path), format="mp4")
        audio_path = video_path.with_suffix(".wav")
        audio.export(str(audio_path), format="wav")
        print(f"✓ Audio extracted to: {audio_path.name} (using pydub)")
        return audio_path
    except ImportError:
        raise Exception(
            "No audio extraction method available. Need one of:\n"
            "  1. FFmpeg installed and in PATH (recommended)\n"
            "  2. moviepy: pip install moviepy\n"
            "  3. pydub: pip install pydub (also requires FFmpeg)"
        )
    except Exception as e:
        raise Exception(f"All audio extraction methods failed. Last error: {e}")


def test_speech():
    """
    Test the speech analyzer with an MP4 file or audio file.
    """
    # Specify your video/audio file here
    video_file = "WIN_20260117_08_33_10_Pro.mp4"  # Replace with your actual filename
    
    # Try to find the file in multiple locations
    possible_paths = [
        Path(__file__).parent / video_file,  # In speech_analysis_module folder
        Path(__file__).parent.parent / "body_language_module" / video_file,  # In body_language_module folder
        Path(__file__).parent.parent / video_file  # In root folder
    ]
    
    video_path = None
    for path in possible_paths:
        if path.exists():
            video_path = path
            break
    
    if video_path is None:
        print(f"Error: File '{video_file}' not found in expected locations")
        print(f"\nSearched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print(f"\nPlease place your MP4 or audio file in one of these locations")
        print(f"and update the video_file variable in this script if needed.\n")
        print("Expected structure:")
        print("speech_analysis_module/")
        print("  ├── speech_analyzer.py")
        print("  ├── test_speech.py")
        print("  └── your_video.mp4  (or .wav, .mp3, .m4a)")
        return
    
    print("=" * 60)
    print("Speech Confidence Analysis Test")
    print("=" * 60)
    print(f"\nFile: {video_file}")
    
    # Determine if we need to extract audio
    audio_path = video_path
    if video_path.suffix.lower() == ".mp4":
        try:
            audio_path = extract_audio_from_mp4(video_path)
            print()  # Empty line for spacing
        except Exception as e:
            print(f"\n✗ Failed to extract audio from MP4: {e}")
            print("\n" + "=" * 60)
            print("SOLUTION: Install FFmpeg to extract audio from MP4 files")
            print("=" * 60)
            print("\nFFmpeg is required to extract audio from video files.")
            print("\nInstall FFmpeg:")
            print("  Windows:")
            print("    1. Download from: https://ffmpeg.org/download.html")
            print("    2. Extract and add 'bin' folder to your system PATH")
            print("    3. Restart your terminal/IDE")
            print("  Mac:     brew install ffmpeg")
            print("  Linux:   sudo apt-get install ffmpeg")
            print("\nAlternatively:")
            print("  - Convert your MP4 to WAV format manually")
            print("  - Use an online converter (MP4 to WAV)")
            print("  - Use VLC or another media player to extract audio")
            print("\n" + "=" * 60)
            print("Skipping analysis - cannot proceed without audio extraction.")
            print("=" * 60)
            return
    else:
        print(f"Using audio file: {audio_path.name}\n")
    
    try:
        # Run analysis
        print("Analyzing speech confidence...")
        results = analyze_speech(str(audio_path))
        
        # Display results - only show confidence score, assessment, interpretation, and recommendations
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"\nConfidence Score: {results['confidence_score']} (0-1 scale)")
        print(f"Assessment: {results['assessment']}")
        print(f"\nInterpretation:\n  {results['interpretation']}")
        
        # Recommendations
        print("\n" + "-" * 60)
        print("RECOMMENDATIONS")
        print("-" * 60)
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 60)
        
        # Optional: Save results to JSON
        output_file = video_path.parent / f"{video_path.stem}_speech_confidence_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")
        
        # Cleanup: Remove extracted WAV file if it was created from MP4
        if video_path.suffix.lower() == ".mp4" and audio_path != video_path and audio_path.exists():
            try:
                audio_path.unlink()
                print(f"Cleaned up temporary audio file: {audio_path.name}")
            except:
                pass
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_speech()
