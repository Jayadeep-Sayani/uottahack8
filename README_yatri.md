# ElevenLabs Text-to-Speech Project

A Python project for generating natural-sounding speech from text using the ElevenLabs API.

## Features

- 🎙️ High-quality text-to-speech conversion
- 🔧 Customizable voice settings (stability, similarity, style)
- 📁 Automatic audio file management
- 🎭 Support for multiple voices
- 💬 Easy-to-use Python class interface

## Setup

### 1. Create a Virtual Environment (Recommended)

**Option A: Using the setup script (Windows)**

```bash
# For PowerShell
.\setup_venv.ps1

# For Command Prompt
setup_venv.bat
```

**Option B: Manual setup**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows Command Prompt:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

Once your virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Get Your ElevenLabs API Key

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Navigate to [API Settings](https://elevenlabs.io/app/settings/api-keys)
3. Copy your API key

### 3. Configure Environment Variables

Open the `.env` file and replace `your_api_key_here` with your actual API key:

```env
ELEVENLABS_API_KEY=your_actual_api_key_here
```

## Usage

### Basic Usage

Run the example script:

```bash
python text_to_speech.py
```

This will generate three example audio files in the `output/` directory.

### Custom Usage

```python
from text_to_speech import TextToSpeech

# Initialize the client
tts = TextToSpeech()

# Generate speech
tts.generate_speech(
    text="Hello, world!",
    output_filename="my_audio.mp3"
)

# List available voices
tts.list_available_voices()
```

### Voice Settings

You can customize the voice output with these parameters:

- **stability** (0.0 - 1.0): Controls consistency
  - Lower = more variable/expressive
  - Higher = more stable/consistent
  
- **similarity_boost** (0.0 - 1.0): Voice similarity to original
  - Higher = closer to the original voice
  
- **style** (0.0 - 1.0): Style exaggeration
  - Higher = more exaggerated delivery
  
- **use_speaker_boost** (bool): Enable for better quality

### Example with Custom Settings

```python
# Expressive, emotional speech
tts.generate_speech(
    text="This is incredible!",
    stability=0.3,
    style=0.6,
    output_filename="excited.mp3"
)

# Professional, consistent speech
tts.generate_speech(
    text="Welcome to the presentation.",
    stability=0.8,
    style=0.0,
    output_filename="professional.mp3"
)
```

## Popular Voice IDs

- **Rachel**: `21m00Tcm4TlvDq8ikWAM` (Default)
- **Drew**: `29vD33N1CtxCmqQRPOHJ`
- **Clyde**: `2EiwWnXFnvU5JabPnv8n`

You can find more voices by running the script or checking your ElevenLabs dashboard.

## Project Structure

```
uottahack8/
├── .env                 # Environment variables (API key)
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── text_to_speech.py   # Main TTS script
├── setup_venv.bat      # Windows batch setup script
├── setup_venv.ps1      # PowerShell setup script
├── README.md           # This file
├── venv/               # Virtual environment (created after setup)
└── output/             # Generated audio files (created automatically)
```

## Troubleshooting

### "API key not found" Error

Make sure you've:
1. Created a `.env` file in the project root
2. Added your API key: `ELEVENLABS_API_KEY=your_key_here`
3. Replaced `your_api_key_here` with your actual key

### Import Errors

Run: `pip install -r requirements.txt`

### Audio Quality Issues

Try adjusting the voice settings:
- Increase `similarity_boost` for better voice quality
- Enable `use_speaker_boost=True`
- Use the latest model: `eleven_multilingual_v2`

## Resources

- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [API Reference](https://elevenlabs.io/docs/api-reference)
- [Voice Lab](https://elevenlabs.io/voice-lab) - Create custom voices

## License

This project is open source and available for educational purposes.
