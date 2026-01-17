# ElevenLabs TTS & STT Tool

A lightweight Python tool for high-quality **Text-to-Speech** (TTS) and **Speech-to-Text** (STT) using ElevenLabs API.

## 🚀 Quick Setup

### 1. Environment & Dependencies
```bash
# Setup virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# Or run .\setup_venv.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Configuration
Create/Update `.env` in the root folder:
```env
ELEVENLABS_API_KEY=your_api_key_here
```

---

## 🎙️ Usage

### Text-to-Speech (TTS)
Convert text into natural sounding audio files.
```bash
python text_to_speech.py
```
- Outputs saved to `output/`
- Edit script to customize voice settings (stability, style, etc.)

### Speech-to-Text (STT / Scribe)
Transcribe audio or video (MP4) files into text.
```bash
python speech_to_text.py
```
1. Enter your file path when prompted.
2. If video (e.g., MP4), it automatically extracts audio using **ffmpeg**.
3. Transcripts saved to `output/`.

> [!IMPORTANT]
> **Video transcription** requires `ffmpeg`. Install via `winget install ffmpeg` on Windows.

---

## 📂 Project Structure
- `text_to_speech.py`: TTS generation logic.
- `speech_to_text.py`: Scribe transcription logic (requires `requests`).
- `.env`: API key & config.
- `output/`: Where your files are saved.
