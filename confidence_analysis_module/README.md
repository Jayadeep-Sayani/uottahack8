# Speech Analysis Module

A Python module that analyzes audio files to assess confidence level in speech during interviews.

## Features

- **Confidence Analysis**: Assesses confidence indicators through speech patterns, hedging words, and sentence structure
- **Audio Transcription**: Converts speech to text using SpeechRecognition (Google Speech API or offline Sphinx)

## Installation

```bash
pip install -r requirements.txt
```

### Additional Requirements

For MP3/M4A support, you may need FFmpeg:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## Usage

### Basic Usage

```python
from speech_analyzer import SpeechAnalyzer

# Initialize analyzer
analyzer = SpeechAnalyzer()

# Analyze audio file
results = analyzer.analyze_audio("recording.wav")

# Print results
print(f"Assessment: {results['assessment']}")
print(f"Overall Score: {results['overall_score']}")
print(f"Interpretation: {results['interpretation']}")
print(f"Recommendations: {results['recommendations']}")
```

### Using Convenience Function

```python
from speech_analyzer import analyze_speech

results = analyze_speech("recording.wav")
```

## Output Format

The analyzer returns a dictionary with the following structure:

```python
{
    "status": "Analysis Complete",
    "confidence_score": 0.742,  # 0-1 score
    "assessment": "MODERATELY_CONFIDENT",  # CONFIDENT, MODERATELY_CONFIDENT, SOMEWHAT_UNCERTAIN, or UNCERTAIN
    "interpretation": "Moderate confidence - generally clear communication with minor uncertainty markers",
    "details": {
        "confidence": {
            "score": 0.72,
            "assessment": "MODERATELY_CONFIDENT",
            "details": {
                "hedging_words_count": 1,
                "repeated_phrases_count": 0,
                "avg_sentence_length": 12.5,
                "question_count": 0
            }
        },
        "audio_duration_seconds": 45.3,
        "total_words": 142,
        "transcription_preview": "First 200 characters of transcribed text..."
    },
    "recommendations": [
        "List of actionable recommendations for improvement"
    ]
}
```

## Confidence Scoring Breakdown

### Confidence Score (0-1)
Based on multiple factors:
- **Hedging words usage**: ("maybe", "perhaps", "I think") - reduces confidence score
- **Repeated words/phrases**: Indicates hesitation - reduces confidence score
- **Sentence structure**: Complete sentences (8-25 words) - increases confidence score
- **Question marks**: Uncertainty indicators - reduces confidence score if >20% of sentences are questions

### Confidence Levels
- **CONFIDENT** (≥0.75): High confidence, clear and assertive communication
- **MODERATELY_CONFIDENT** (0.55-0.74): Good confidence with minor uncertainty markers
- **SOMEWHAT_UNCERTAIN** (0.35-0.54): Lower confidence with noticeable hesitation
- **UNCERTAIN** (<0.35): Low confidence, needs improvement in assertive communication

## Supported Audio Formats

- **Primary**: WAV files (direct support)
- **With pydub**: MP3, M4A, FLAC, and other formats supported by FFmpeg

## Notes

- The module uses Google Speech Recognition API by default (free for limited use)
- Falls back to offline Sphinx recognition if Google API is unavailable
- Audio quality affects transcription accuracy - use clear recordings for best results
- For MP3/M4A files, ensure FFmpeg is installed for format conversion
