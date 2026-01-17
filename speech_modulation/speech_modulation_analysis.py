"""
AssemblyAI Speech Modulation Analysis

Analyzes MP4 videos/audio for:
- Transcription with disfluencies (fillers like 'um', 'uh')
- Sentiment Analysis (Positive, Negative, Neutral)
- Prosody & Speech Rate (WPM, pauses)
"""

import os
import time
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv
import assemblyai as aai

# Load environment variables
load_dotenv()

class SpeechModulationAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("AssemblyAI API key not found. Please set ASSEMBLYAI_API_KEY in .env")
        
        aai.settings.api_key = self.api_key
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def extract_audio(self, video_path):
        """Extracts audio from video file using ffmpeg."""
        video_path = Path(video_path)
        audio_path = self.output_dir / f"{video_path.stem}_temp_audio.mp3"
        
        print(f"📦 Extracting audio from {video_path.name}...")
        try:
            subprocess.run([
                "ffmpeg", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", "-y", str(audio_path)
            ], check=True, capture_output=True)
            return str(audio_path)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg Error: {e.stderr.decode()}")
            raise

    def analyze(self, file_path):
        """Runs full analysis on the given file."""
        file_path = Path(file_path)
        
        # Extract audio if video
        if file_path.suffix.lower() == ".mp4":
            audio_file = self.extract_audio(file_path)
        else:
            audio_file = str(file_path)

        print(f"🚀 Starting AssemblyAI analysis for {file_path.name}...")

        config = aai.TranscriptionConfig(
            disfluencies=True,          # Detect "um", "uh", etc.
            sentiment_analysis=True,     # Detect Positive/Negative/Neutral
            speaker_labels=True          # Distinguish speakers
        )

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file, config)

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription error: {transcript.error}")

        # Post-process for "Modulation" features
        analysis_results = self.get_modulation_metrics(transcript)
        
        # Save results
        output_file = self.output_dir / f"{file_path.stem}_modulation_analysis.json"
        with open(output_file, "w") as f:
            json.dump(analysis_results, f, indent=4)

        print(f"✅ Analysis complete! Results saved to {output_file}")
        self.print_summary(analysis_results)
        return analysis_results

    def get_modulation_metrics(self, transcript):
        """Calculates prosody, speech rate, and pause metrics from transcript data."""
        words = transcript.words
        if not words:
            return {}

        total_words = len(words)
        duration_minutes = transcript.audio_duration / 60.0
        wpm = total_words / duration_minutes if duration_minutes > 0 else 0

        # Detect pauses (gaps > 1 second between words)
        pauses = []
        fillers = []
        filler_list = ["um", "uh", "hmm", "mhm", "uh-huh", "ah", "huh", "m"]

        for i in range(len(words) - 1):
            gap = (words[i+1].start - words[i].end) / 1000.0 # Convert ms to s
            if gap > 1.0:
                pauses.append({
                    "after_word": words[i].text,
                    "duration_sec": round(gap, 2),
                    "timestamp_ms": words[i].end
                })
            
            if words[i].text.lower().strip(",.") in filler_list:
                fillers.append({
                    "word": words[i].text,
                    "timestamp_ms": words[i].start
                })

        # Sentiment Summary
        sentiments = [s.sentiment for s in transcript.sentiment_analysis]
        sentiment_summary = {
            "positive": sentiments.count("POSITIVE"),
            "neutral": sentiments.count("NEUTRAL"),
            "negative": sentiments.count("NEGATIVE")
        }

        return {
            "summary": {
                "speech_rate_wpm": round(wpm, 2),
                "total_filler_words": len(fillers),
                "significant_pauses": len(pauses),
                "primary_sentiment": max(sentiment_summary, key=sentiment_summary.get),
            },
            "sentiment_details": sentiment_summary,
            "fillers": fillers,
            "pauses": pauses,
            "transcript": transcript.text
        }

    def print_summary(self, results):
        s = results["summary"]
        print("\n" + "="*40)
        print("📊 SPEECH MODULATION SUMMARY")
        print("="*40)
        print(f"⏱️  Speech Rate:      {s['speech_rate_wpm']} WPM")
        print(f"🗣️  Filler Words:     {s['total_filler_words']} detected")
        print(f"🛑  Long Pauses:      {s['significant_pauses']} matches")
        print(f"😊  Main Sentiment:   {s['primary_sentiment'].upper()}")
        print("="*40 + "\n")

if __name__ == "__main__":
    # Example usage
    import sys
    
    analyzer = None
    try:
        analyzer = SpeechModulationAnalyzer()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    file_to_analyze = input("Enter path to video/audio file: ").strip().strip('"').strip("'")
    if os.path.exists(file_to_analyze):
        analyzer.analyze(file_to_analyze)
    else:
        print(f"❌ File not found: {file_to_analyze}")
