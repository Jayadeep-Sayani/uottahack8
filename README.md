# Get-into.tech

**Get-into.tech** is an AI-powered interview preparation platform. It generates personalized interview questions using Google Gemini, converts them to high-quality audio with ElevenLabs, and provides deep analysis of candidate performance using vision and speech analysis modules.

## Architecture & Modules

The project consists of a Flask backend API, several Python analysis modules, and a React frontend:

- **Frontend**: Vite + React UI for the interview experience.
- **Backend (`server.py`)**: Flask API orchestrating the interview flow.
- **CLI (`main.py`)**: Command-line tool for question generation and analysis.
- **Analysis Modules**:
  - `body_language_module/`: Video analysis using MediaPipe pose detection.
  - `confidence_analysis_module/`: Audio analysis for speech confidence.
  - `speech_modulation/`: Advanced speech pattern analysis via AssemblyAI.
  - `gemini_question_gen/`: Question generation logic.
  - `eleven_labs_tts/`: Text-to-speech integration.

---

## Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+
- **FFmpeg**: Required for audio extraction from video recordings.
  - *Windows*: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html).
  - *macOS*: `brew install ffmpeg`
  - *Linux*: `sudo apt install ffmpeg`

---

## Installation & Setup

### 1. Environment Configuration
Create a `.env` file in the repository root:

```env
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
# Optional
DEFAULT_VOICE_ID=optional_voice_id
```

### 2. Backend Setup
From the repository root:

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```powershell
cd Frontend
npm install
```

---

## Usage

### Running the Web Application (Recommended)
This launches the full interactive interview experience.

1. **Start the Backend Server**:
   ```powershell
   # In the root directory (with venv active)
   python server.py
   ```
   *Server runs on `http://localhost:5000`*

2. **Start the Frontend Development Server**:
   ```powershell
   cd Frontend
   npm run dev
   ```
   *App runs on `http://localhost:5173`*

---

## Notes
- **API Keys**: Ensure all keys in `.env` are valid; otherwise, modules may fall back to default/simulated behavior.
- **Hardware Access**: The frontend requires Webcam and Microphone permissions to record responses.
- **Analysis Results**: JSON analysis reports are generated in the same directory as the recordings (usually `user_recordings/` or the root).
