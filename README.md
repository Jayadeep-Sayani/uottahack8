# Get-Into
### Emotionally Intelligent AI Interview Coaching

## About the Project

### Inspiration
Interviews aren’t just about *what* you say — they’re about *how* you say it. Confidence, anxiety, tone, and delivery heavily influence hiring decisions, yet most interview prep tools only evaluate content.

As students and early-career engineers, we’ve all experienced interview stress. Practicing with friends doesn’t replicate real pressure, and existing platforms provide generic, static feedback. We were inspired to build **Get-Into** after realizing no tool today combines emotional awareness, fair feedback, and personalized interview coaching.

Our goal was simple: **create an interview practice experience that actually feels like a real interview.**

---

## What It Does

**Get-Into** is an emotionally intelligent AI mock interview platform that simulates real interview pressure while providing empathetic, actionable feedback.

It can:
- Generate **company-specific interview questions** from real job descriptions
- Conduct **live mock interviews** using an AI avatar with voice
- Track **biometric and behavioral signals** like engagement, posture, and stress in real time
- Adapt its **tone and feedback** based on the user’s emotional state
- Produce a **post-session report** combining content quality *and* delivery insights

Instead of saying:
> “Your answer was weak.”

Get-Into says:
> “Your confidence dipped during this question — let’s work on that.”

---

## How We Built It

Get-Into is designed as a **multi-agent AI system** where reasoning and emotional signals work together.

### Architecture
- **Frontend:** React + Vite + TailwindCSS  
  - Single-page experience  
  - Webcam and microphone access
- **Backend:** Python + Flask  
  - Real-time interview orchestration
- **AI Reasoning:** Gemini API  
  - Job description analysis  
  - Tailored interview question generation  
  - Feedback synthesis
- **Agent Orchestration:** LangGraph  
  - Manages interview state, sensing, analysis, and feedback agents
- **Biometrics & Engagement:** OpenCV  
  - Stress detection  
  - Breathing patterns  
  - Engagement signals via webcam
- **Voice & Presence:** ElevenLabs  
  - Realistic AI interviewer voice  
  - Encouragement and feedback delivery
- **Data Storage:** MongoDB Atlas  
  - Session history  
  - Feedback tracking
- **Deployment:** DigitalOcean  

Each interview runs as a structured flow where **content analysis and emotional signals are evaluated together**, not separately.

---

## Challenges We Ran Into

- **Real-time biometric integration**  
  Synchronizing live webcam signals while handling fallbacks gracefully
- **Latency management**  
  Coordinating voice output, sensing data, and AI responses without breaking immersion
- **Prompt engineering**  
  Teaching the AI to be empathetic instead of robotic required multiple iterations
- **Webcam permissions & browser quirks**  
  Navigating strict browser security constraints
- **Scope control**  
  Balancing ambitious features with hackathon time limits

---

## Accomplishments We’re Proud Of

- Built a **first-of-its-kind emotionally aware interview coach**
- Successfully combined **biometric data and LLM reasoning** into a single feedback loop
- Created a realistic interview presence using **voice instead of text**
- Delivered **actionable insights** beyond surface-level scoring
- Designed a clean demo flow judges can experience in **under 3 minutes**

---

## What We Learned

- Emotional intelligence dramatically improves AI usefulness
- AI systems require strong **state management** and graceful fallbacks
- Biometrics add powerful context but must be interpreted carefully
- **Multi-agent architectures** (LangGraph) are ideal for adaptive experiences
- Great UX matters just as much as great models

> AI feels most human when it responds to how people feel, not just what they say.

---

## What’s Next for Get-Into

- Multi-round interview simulations (phone → behavioral → technical)
- Adaptive follow-up questions based on detected weaknesses
- Audio replay with biometric overlays
- Confidence-building drills and guided breathing exercises
- Gamified progress tracking and rewards
- Support for non-native speakers and accessibility features

Our long-term vision is to make **high-quality interview coaching accessible, empathetic, and personalized for everyone**.

---

## Built With

- React  
- Vite  
- TailwindCSS  
- Python  
- Flask  
- Gemini API  
- LangGraph  
- OpenCV  
- ElevenLabs  
- MongoDB Atlas  
- DigitalOcean  

---

✨ **Get-Into isn’t just interview prep — it’s confidence training powered by emotionally intelligent AI.**
