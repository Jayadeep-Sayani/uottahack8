# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Get-into.tech** - An AI-powered interview preparation platform that generates personalized interview questions and analyzes candidate performance through voice, body language, and speech patterns.

## Architecture

The project consists of a Flask backend API with multiple Python analysis modules and a React frontend:

```
├── main.py                      # Flask API server (port 5000)
├── Frontend/                    # React + Vite frontend
├── gemini_question_gen/         # Interview question generation (Gemini API)
├── eleven_labs_tts/             # Text-to-speech (ElevenLabs API)
├── body_language_module/        # Video analysis (MediaPipe pose detection)
├── confidence_analysis_module/  # Speech confidence analysis
├── speech_modulation/           # Speech pattern analysis (AssemblyAI)
├── interview_output/            # Generated audio files
└── user_recordings/             # User response recordings
```

### Data Flow
1. User submits company name + job description via frontend
2. Backend generates 5 questions (1 intro, 2 regular, 2 situational) using Gemini
3. ElevenLabs converts questions to audio MP3s
4. User records video responses
5. Backend analyzes responses for body language, eye contact, speech confidence, and speech modulation
6. Results returned as JSON

## Development Commands

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask server (requires API keys in .env)
python main.py
```

### Frontend
```bash
cd Frontend
npm install
npm run dev      # Development server
npm run build    # Production build
npm run lint     # ESLint
```

## Required Environment Variables (.env)

```
GEMINI_API_KEY=<Google Gemini API key>
ELEVENLABS_API_KEY=<ElevenLabs API key>
ASSEMBLYAI_API_KEY=<AssemblyAI API key>
SENTRY_DSN=<Sentry DSN for backend>
```

For the frontend, create `Frontend/.env`:
```
VITE_SENTRY_DSN=<Sentry DSN for frontend>
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/start-interview` | POST | Generate questions and audio from company/job info |
| `/api/audio/<filename>` | GET | Serve generated audio files |
| `/api/save-user-recording` | POST | Save user's recorded responses |
| `/api/health` | GET | Health check |

## Key Dependencies

- **Video Processing**: OpenCV, MediaPipe (pose estimation)
- **Audio**: ElevenLabs SDK, SpeechRecognition, pydub, AssemblyAI
- **AI**: google-generativeai (Gemini)
- **External Tool**: FFmpeg required for MP4 audio extraction

## Frontend Routes

- `/` - Landing page
- `/Job-Info` - Interview setup form (company + job description)
- `/interview` - Interview session page

## Sentry Monitoring

The project is instrumented with Sentry for error tracking and performance monitoring.

**Backend** (Flask): Tracks API errors, performance traces for all endpoints, and custom spans for:
- `ai.generate` - Gemini question generation
- `ai.tts` - ElevenLabs text-to-speech conversion
- `analysis.*` - Body language, eye contact, speech confidence, and speech modulation analysis

**Frontend** (React): Tracks JavaScript errors, browser performance, and session replays on errors.

Get your DSN from [Sentry](https://sentry.io) after creating a project.
