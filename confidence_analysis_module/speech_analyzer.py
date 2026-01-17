"""
Speech Analysis Module

Analyzes audio files to evaluate confidence level in speech.

Uses SpeechRecognition for transcription and analyzes confidence indicators.
"""

import speech_recognition as sr
import wave
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import re
import struct


class SpeechAnalyzer:
    """
    Analyzes vocal confidence level in speech from audio files.
    Evaluates confidence based on how they sound: pause patterns, filler sounds, speech rate, and fluency.
    Focuses on acoustic/vocal features, not word content.
    """
    
    def __init__(self):
        """Initialize speech recognizer."""
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise and energy threshold
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # Metrics tracking
        self.transcribed_text = ""
        self.audio_duration = 0.0
        self.word_count = 0
        self.audio_path = None
        
    def analyze_audio(self, audio_path: str) -> Dict:
        """
        Analyze confidence level in an audio file.
        
        Args:
            audio_path: Path to the audio file (WAV, MP3, or M4A)
        
        Returns:
            Dictionary with confidence analysis results
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Reset metrics
        self.transcribed_text = ""
        self.audio_duration = 0.0
        self.word_count = 0
        self.audio_path = audio_path
        
        print(f"Analyzing audio: {audio_path.name}")
        
        # Get audio duration
        try:
            self.audio_duration = self._get_audio_duration(audio_path)
        except Exception as e:
            print(f"Warning: Could not get audio duration: {e}")
            pass
        
        # Transcribe audio
        try:
            print("Transcribing audio...")
            self.transcribed_text = self._transcribe_audio(audio_path)
            
            if not self.transcribed_text or len(self.transcribed_text.strip()) == 0:
                return {
                    "confidence_score": 0,
                    "assessment": "UNABLE_TO_ANALYZE",
                    "interpretation": "No speech detected in audio file",
                    "recommendations": ["Ensure audio contains clear speech"]
                }
            
            print(f"Transcribed: {self.transcribed_text[:100]}...")
            
        except sr.UnknownValueError:
            return {
                "confidence_score": 0,
                "assessment": "UNABLE_TO_ANALYZE",
                "interpretation": "Audio could not be transcribed - speech may be unclear or file may be corrupted",
                "recommendations": ["Ensure audio is clear and contains speech"]
            }
        except Exception as e:
            return {
                "confidence_score": 0,
                "assessment": "ERROR",
                "interpretation": f"Error during transcription: {str(e)}",
                "recommendations": [f"Check audio file format and quality: {str(e)}"]
            }
        
        # Analyze confidence based on vocal/acoustic features
        confidence_analysis = self._analyze_confidence()
        
        # Compile results
        results = self._compile_analysis(confidence_analysis)
        
        return results
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Duration in seconds
        """
        try:
            # Try WAV first
            if audio_path.suffix.lower() == ".wav":
                with wave.open(str(audio_path), "rb") as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration = frames / float(sample_rate)
                    return duration
        except:
            pass
        
        # For other formats, try using pydub if available
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except ImportError:
            # If pydub not available, we'll estimate from transcription
            pass
        except Exception:
            pass
        
        # Fallback: estimate 5 seconds per 100 words as rough estimate
        return 0.0
    
    def _transcribe_audio(self, audio_path: Path) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Transcribed text
        """
        # Convert audio to WAV if needed
        if audio_path.suffix.lower() != ".wav":
            # Try using pydub to convert
            try:
                from pydub import AudioSegment
                wav_path = audio_path.with_suffix(".wav")
                audio = AudioSegment.from_file(str(audio_path))
                audio.export(str(wav_path), format="wav")
                audio_path = wav_path
            except ImportError:
                # If pydub not available, try direct loading
                pass
            except Exception as e:
                print(f"Warning: Could not convert audio: {e}")
        
        # Load audio file
        audio = None
        try:
            with sr.AudioFile(str(audio_path)) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
        except Exception as e:
            # Try alternative method
            try:
                with sr.AudioFile(str(audio_path)) as source:
                    audio = self.recognizer.record(source)
            except Exception as e2:
                raise Exception(f"Could not load audio file: {e2}")
        
        if audio is None:
            raise Exception("Could not load audio from file")
        
        # Try Google Speech Recognition (free, no API key needed for small amounts)
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            # Try alternative recognition engines
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except:
                raise sr.UnknownValueError("Could not understand audio")
        except sr.RequestError as e:
            # Fallback to sphinx if Google fails
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except:
                raise Exception(f"Recognition service error: {e}")
    
    def _analyze_pauses(self, audio_path: Path) -> Dict:
        """
        Analyze pause patterns in audio file.
        Long pauses indicate hesitation/uncertainty.
        
        Returns:
            Dictionary with pause analysis
        """
        try:
            # Try to read WAV file for pause analysis
            if audio_path.suffix.lower() != ".wav":
                # Try to find converted WAV file
                wav_path = audio_path.with_suffix(".wav")
                if wav_path.exists():
                    audio_path = wav_path
                else:
                    return {"pause_count": 0, "long_pause_count": 0, "avg_pause_duration": 0, "total_pause_time": 0}
            
            with wave.open(str(audio_path), 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                frames = wav_file.getnframes()
                
                # Read audio data
                audio_data = wav_file.readframes(frames)
                sample_width = wav_file.getsampwidth()
                
                # Convert to numpy array
                if sample_width == 1:
                    audio_array = np.frombuffer(audio_data, dtype=np.uint8).astype(np.float32) - 128
                elif sample_width == 2:
                    audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                else:
                    return {"pause_count": 0, "long_pause_count": 0, "avg_pause_duration": 0, "total_pause_time": 0}
                
                # Calculate energy (RMS) for each chunk
                chunk_size = int(sample_rate * 0.1)  # 100ms chunks
                energy_threshold = np.std(audio_array) * 0.1  # Threshold for silence
                
                energies = []
                for i in range(0, len(audio_array), chunk_size):
                    chunk = audio_array[i:i+chunk_size]
                    if len(chunk) > 0:
                        energy = np.sqrt(np.mean(chunk**2))
                        energies.append(energy)
                
                # Detect pauses (low energy segments)
                is_silent = [e < energy_threshold for e in energies]
                
                # Find speech boundaries - ignore silence at beginning and end
                speech_start_idx = 0
                speech_end_idx = len(is_silent) - 1
                
                # Find where speech actually starts (first non-silent chunk)
                for i, silent in enumerate(is_silent):
                    if not silent:
                        speech_start_idx = i
                        break
                
                # Find where speech actually ends (last non-silent chunk)
                for i in range(len(is_silent) - 1, -1, -1):
                    if not is_silent[i]:
                        speech_end_idx = i
                        break
                
                # Only analyze pauses between speech boundaries (ignore leading/trailing silence)
                speech_segment = is_silent[speech_start_idx:speech_end_idx + 1]
                
                # Count pause segments within speech
                pause_segments = []
                in_pause = False
                pause_start = 0
                
                for i, silent in enumerate(speech_segment):
                    if silent and not in_pause:
                        in_pause = True
                        pause_start = i
                    elif not silent and in_pause:
                        in_pause = False
                        pause_duration = (i - pause_start) * 0.1  # Convert to seconds
                        if pause_duration > 0.2:  # Only count pauses > 200ms
                            pause_segments.append(pause_duration)
                
                # Calculate statistics
                pause_count = len(pause_segments)
                long_pause_count = sum(1 for p in pause_segments if p > 1.0)  # Pauses > 1 second
                total_pause_time = sum(pause_segments) if pause_segments else 0
                avg_pause_duration = total_pause_time / pause_count if pause_count > 0 else 0
                
                return {
                    "pause_count": pause_count,
                    "long_pause_count": long_pause_count,
                    "avg_pause_duration": round(avg_pause_duration, 2),
                    "total_pause_time": round(total_pause_time, 2)
                }
        except Exception as e:
            # If audio analysis fails, return default values
            return {"pause_count": 0, "long_pause_count": 0, "avg_pause_duration": 0, "total_pause_time": 0}
    
    def _analyze_confidence(self) -> Dict:
        """
        Analyze confidence level based on how they sound (acoustic/vocal features):
        - Pause patterns (long pauses = hesitation/uncertainty)
        - Filler sounds (um, uh - hesitation markers)
        - Speech rate consistency (choppy = less confident)
        - Fluency (smooth flow = more confident)
        
        Returns:
            Dictionary with confidence analysis
        """
        if not self.transcribed_text or self.audio_duration == 0:
            return {
                "score": 0,
                "assessment": "N/A"
            }
        
        text = self.transcribed_text
        words = text.split()
        self.word_count = len(words)
        
        # Analyze pauses in audio (acoustic feature)
        pause_analysis = self._analyze_pauses(self.audio_path) if self.audio_path else {
            "pause_count": 0, "long_pause_count": 0, "avg_pause_duration": 0, "total_pause_time": 0
        }
        
        # Detect filler sounds (acoustic hesitation markers)
        # These are transcribed as "um", "uh", "er", "ah", "eh"
        filler_sounds = ["um", "uh", "er", "ah", "eh", "hmm"]
        text_lower = text.lower()
        filler_count = 0
        for filler in filler_sounds:
            pattern = r'\b' + re.escape(filler) + r'\b'
            filler_count += len(re.findall(pattern, text_lower))
        
        # Calculate speech rate (words per second)
        words_per_second = self.word_count / self.audio_duration if self.audio_duration > 0 else 0
        
        # Calculate pause ratio (time spent pausing vs. speaking)
        speech_time = self.audio_duration - pause_analysis["total_pause_time"]
        pause_ratio = pause_analysis["total_pause_time"] / self.audio_duration if self.audio_duration > 0 else 0
        
        # Calculate confidence score based on vocal/acoustic features
        confidence_score = 1.0
        
        # Penalize long pauses (indicates hesitation/uncertainty)
        # More lenient: Accept up to 40% pausing before significant penalty
        if pause_ratio > 0.50:  # More than 50% time pausing (very high)
            pause_penalty = min(0.4, (pause_ratio - 0.50) * 1.5)
            confidence_score -= pause_penalty
        elif pause_ratio > 0.40:  # 40-50% pausing (moderate penalty)
            pause_penalty = (pause_ratio - 0.40) * 0.8
            confidence_score -= pause_penalty
        elif pause_ratio > 0.30:  # 30-40% pausing (minor penalty)
            pause_penalty = (pause_ratio - 0.30) * 0.5
            confidence_score -= pause_penalty
        
        # Penalize frequent long pauses (>1 second)
        # More lenient: Accept more long pauses before penalty
        if self.audio_duration > 0:
            long_pause_rate = pause_analysis["long_pause_count"] / (self.audio_duration / 30.0)
            if long_pause_rate > 5:  # More than 5 long pauses per 30 seconds (very high)
                confidence_score -= min(0.25, (long_pause_rate - 5) * 0.05)
            elif long_pause_rate > 3:  # 3-5 long pauses per 30 seconds (moderate)
                confidence_score -= min(0.15, (long_pause_rate - 3) * 0.07)
        
        # Penalize filler sounds (acoustic hesitation)
        # More lenient: Accept up to 5% filler sounds before penalty
        if self.word_count > 0:
            filler_rate = (filler_count / self.word_count) * 100
            if filler_rate > 8:  # More than 8% filler sounds (high)
                confidence_score -= min(0.3, (filler_rate - 8) * 0.04)
            elif filler_rate > 5:  # 5-8% filler sounds (moderate)
                confidence_score -= min(0.2, (filler_rate - 5) * 0.06)
        
        # Penalize very slow or very fast speech (suggests uncertainty or nervousness)
        # More lenient: Wider acceptable range (100-220 WPM = 1.67-3.67 words per second)
        if words_per_second < 1.0:  # Very slow (< 60 WPM)
            confidence_score -= min(0.25, (1.0 - words_per_second) * 0.15)
        elif words_per_second < 1.67:  # Slow (60-100 WPM) - minor penalty
            confidence_score -= min(0.15, (1.67 - words_per_second) * 0.2)
        elif words_per_second > 5.0:  # Very fast (> 300 WPM)
            confidence_score -= min(0.2, (words_per_second - 5.0) * 0.08)
        elif words_per_second > 3.67:  # Fast (220-300 WPM) - minor penalty
            confidence_score -= min(0.15, (words_per_second - 3.67) * 0.1)
        
        # Penalize high pause count (choppy speech)
        # More lenient: Accept more pauses before penalty
        if self.word_count > 0:
            pause_rate = (pause_analysis["pause_count"] / self.word_count) * 10
            if pause_rate > 3.0:  # More than 3 pauses per 10 words (very choppy)
                confidence_score -= min(0.25, (pause_rate - 3.0) * 0.15)
            elif pause_rate > 2.0:  # 2-3 pauses per 10 words (choppy)
                confidence_score -= min(0.15, (pause_rate - 2.0) * 0.15)
        
        # Normalize score
        confidence_score = max(0, min(1, confidence_score))
        
        # Determine assessment
        if confidence_score >= 0.75:
            assessment = "CONFIDENT"
        elif confidence_score >= 0.55:
            assessment = "MODERATELY_CONFIDENT"
        elif confidence_score >= 0.35:
            assessment = "SOMEWHAT_UNCERTAIN"
        else:
            assessment = "UNCERTAIN"
        
        return {
            "score": round(confidence_score, 3),
            "assessment": assessment,
            "details": {
                "pause_count": pause_analysis["pause_count"],
                "long_pause_count": pause_analysis["long_pause_count"],
                "avg_pause_duration": pause_analysis["avg_pause_duration"],
                "pause_ratio": round(pause_ratio * 100, 1),  # Percentage
                "filler_sounds_count": filler_count,
                "filler_rate_per_100_words": round((filler_count / self.word_count * 100) if self.word_count > 0 else 0, 1),
                "speech_rate_wpm": round(words_per_second * 60, 1),  # Words per minute
                "words_per_second": round(words_per_second, 2)
            }
        }
    
    def _compile_analysis(self, confidence: Dict) -> Dict:
        """
        Compile analysis results into a summary.
        
        Args:
            confidence: Confidence analysis results
        
        Returns:
            Dictionary with complete analysis results
        """
        confidence_score = confidence["score"]
        assessment = confidence["assessment"]
        
        # Determine interpretation based on vocal confidence level
        if confidence_score >= 0.75:
            interpretation = "High vocal confidence - speaks with clarity, steady pace, and minimal hesitation"
        elif confidence_score >= 0.55:
            interpretation = "Moderate vocal confidence - generally clear speech with occasional hesitation or pauses"
        elif confidence_score >= 0.35:
            interpretation = "Lower vocal confidence - shows hesitation through pauses, filler sounds, or uneven speech"
        else:
            interpretation = "Low vocal confidence - frequent pauses, hesitations, and disfluency indicate uncertainty in speech"
        
        return {
            "confidence_score": confidence_score,
            "assessment": assessment,
            "interpretation": interpretation,
            "recommendations": self._generate_recommendations(confidence)
        }
    
    def _generate_recommendations(self, confidence: Dict) -> List[str]:
        """
        Generate recommendations based on vocal/acoustic confidence analysis.
        
        Args:
            confidence: Confidence analysis results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        details = confidence.get("details", {})
        confidence_assessment = confidence.get("assessment", "")
        
        # Pause-related recommendations
        pause_count = details.get("pause_count", 0)
        long_pause_count = details.get("long_pause_count", 0)
        pause_ratio = details.get("pause_ratio", 0)
        
        if pause_ratio > 50:
            recommendations.append(f"Consider reducing frequent pausing - {pause_ratio}% of speech time is pauses. Aim for 20-40% pause time.")
        elif pause_ratio > 40:
            recommendations.append("You could reduce pause frequency slightly - this would make speech sound more fluid")
        
        if long_pause_count > 5:
            recommendations.append(f"Try to reduce some long pauses - {long_pause_count} pause(s) longer than 1 second detected. A few long pauses are fine, but many can reduce flow.")
        elif long_pause_count > 3:
            recommendations.append("Consider slightly reducing long pauses for smoother speech flow")
        
        # Filler sounds recommendations
        filler_count = details.get("filler_sounds_count", 0)
        filler_rate = details.get("filler_rate_per_100_words", 0)
        
        if filler_rate > 8:
            recommendations.append(f"Practice reducing filler sounds (um, uh) - {filler_count} filler sounds detected ({filler_rate} per 100 words). Try pausing silently instead.")
        elif filler_rate > 5:
            recommendations.append("You could reduce filler sounds slightly - practice replacing some 'um' and 'uh' with natural pauses")
        elif filler_count > 0:
            recommendations.append("Good speech - you could continue to minimize filler sounds for even more polished speech")
        
        # Speech rate recommendations
        speech_rate = details.get("speech_rate_wpm", 0)
        words_per_second = details.get("words_per_second", 0)
        
        if words_per_second < 1.0:
            recommendations.append(f"Try speaking at a slightly faster pace - current rate is {speech_rate} WPM. A rate of 100-220 WPM sounds more natural.")
        elif words_per_second < 1.67:
            recommendations.append(f"Consider speaking slightly faster - {speech_rate} WPM is a bit slow. A comfortable pace is 100-220 WPM.")
        elif words_per_second > 5.0:
            recommendations.append(f"Consider slowing down slightly - {speech_rate} WPM is quite fast. A comfortable pace is 100-220 WPM.")
        elif words_per_second > 3.67:
            recommendations.append(f"Your pace is good - {speech_rate} WPM. You could slow down slightly (100-220 WPM target) for easier comprehension.")
        
        # Fluency recommendations
        if pause_count > 0 and self.word_count > 0:
            pause_rate = (pause_count / self.word_count) * 10
            if pause_rate > 3.0:
                recommendations.append(f"Try to improve speech fluency - {pause_count} pauses detected makes speech somewhat choppy. Practice speaking more smoothly.")
            elif pause_rate > 2.0:
                recommendations.append("You could improve speech fluency slightly - practice speaking more smoothly between thoughts")
        
        # General recommendations if no specific issues
        if not recommendations:
            if confidence_assessment in ["SOMEWHAT_UNCERTAIN", "UNCERTAIN"]:
                recommendations.append("Continue practicing to improve vocal confidence - focus on speaking with steady pace and minimal hesitation")
            elif confidence_assessment == "MODERATELY_CONFIDENT":
                recommendations.append("Good vocal confidence - continue practicing to reduce hesitation and improve fluency")
            else:
                recommendations.append("Excellent vocal confidence! Maintain steady pace and clear speech.")
        
        return recommendations


def analyze_speech(audio_path: str) -> Dict:
    """
    Convenience function to analyze confidence in speech from an audio file.
    
    Args:
        audio_path: Path to the audio file (WAV, MP3, or M4A)
    
    Returns:
        Dictionary with confidence analysis results
    """
    analyzer = SpeechAnalyzer()
    return analyzer.analyze_audio(audio_path)
