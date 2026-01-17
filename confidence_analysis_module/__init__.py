"""
Speech Analysis Module

Analyzes audio files for vocal confidence level in speech.
Evaluates confidence based on how they sound: pause patterns, filler sounds, speech rate, and fluency.
Focuses on acoustic/vocal features, not word content.
"""

from .speech_analyzer import SpeechAnalyzer, analyze_speech

__all__ = ["SpeechAnalyzer", "analyze_speech"]
