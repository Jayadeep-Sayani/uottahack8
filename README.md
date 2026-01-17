# AInterview

AI-powered mock interview co-pilot. The project generates interview questions
with Gemini and converts them to voice with ElevenLabs, plus optional analysis
modules for body language, confidence, and speech modulation.

## Contents
- `main.py`: orchestrates question generation + TTS output
- `gemini_question_gen/`: Gemini-based question generator
- `eleven_labs_tts/`: ElevenLabs TTS utilities
- `body_language_module/`, `confidence_analysis_module/`, `speech_modulation/`:
  optional analysis modules
- `frontend/`: Vite + React UI

## Requirements
- Python 3.10+ (tested with 3.11+)
- Node.js 18+ for the frontend

## Environment variables
Create a `.env` file in the repo root:

```
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
DEFAULT_VOICE_ID=optional_voice_id
OUTPUT_DIR=optional_output_dir
```

## Backend quick start
From the repo root:

```
python -m venv venv
venv\Scripts\activate
python -m pip install -r gemini_question_gen/requirements.txt
python -m pip install -r eleven_labs_tts/requirements.txt
python main.py
```

Generated audio files are written to `interview_output/`.

## Frontend quick start

```
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173/`.

## Notes
- Some modules include sample outputs and test assets in their folders.
- If you run into webcam/microphone permission errors in the UI, grant browser
  access and reload.
