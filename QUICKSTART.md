# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Set up your virtual environment

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # PowerShell
# OR
venv\Scripts\activate  # Command Prompt
```

### Step 2: Install dependencies

```bash
pip install elevenlabs==1.11.0 python-dotenv==1.0.0
```

### Step 3: Configure your API key

1. Get your API key from [ElevenLabs](https://elevenlabs.io/app/settings/api-keys)
2. Open `.env` file
3. Replace `your_api_key_here` with your actual API key

### Step 4: Run the example

```bash
python text_to_speech.py
```

## ✅ What You Should See

The script will:
- Generate 3 example audio files
- List all available voices
- Save files to the `output/` folder

## 🎯 Next Steps

Check out the full [README_yatri.md](README_yatri.md) for:
- Custom voice settings
- Advanced usage examples
- Troubleshooting tips

## 📝 Quick Example

```python
from text_to_speech import TextToSpeech

tts = TextToSpeech()
tts.generate_speech("Hello, world!", output_filename="hello.mp3")
```

That's it! 🎉
