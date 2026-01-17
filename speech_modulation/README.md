# AssemblyAI Speech Modulation Tool

Analyze speech patterns from MP4 videos using AssemblyAI. Detects prosody, fillers, sentiment, and more.

## 🚀 Setup

1. **Get an API Key**: Sign up at [AssemblyAI](https://www.assemblyai.com/dashboard/).
2. **Configure `.env`**:
   ```env
   ASSEMBLYAI_API_KEY=your_key_here
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎙️ Usage

Run the analysis script:
```bash
python speech_modulation/speech_modulation_analysis.py
```
It will prompt you for an MP4 or audio file path.

### Features Detected:
- **Prosody & Rate**: Calculates Words Per Minute (WPM).
- **Filler Words**: Detects "um", "uh", "ah", etc.
- **Pauses**: Identifies silences longer than 1 second.
- **Sentiment**: Classifies sentences as Positive, Neutral, or Negative.
- **Confidence**: Tracks AI confidence per word.

---

## 📂 Project Structure
- `speech_modulation/`: Contains the analysis logic.
- `output/`: JSON reports are saved here.
- `requirements.txt`: Project dependencies.
