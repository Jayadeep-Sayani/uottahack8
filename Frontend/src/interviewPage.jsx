import React, { useState, useRef, useEffect } from 'react';
import { Camera, Mic, MicOff, Video, VideoOff, MessageSquare } from 'lucide-react';

export default function InterviewPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [subtitle, setSubtitle] = useState('');
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);

  const [questions, setQuestions] = useState([
    "Tell me about yourself and your background.",
    "What interests you most about this opportunity?",
    "Describe a challenging project you've worked on.",
    "How do you handle tight deadlines and pressure?",
    "Where do you see yourself in five years?"
  ]);

  useEffect(() => {
    // Try to load questions from localStorage
    const storedData = localStorage.getItem('interviewData');
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        if (parsedData.questionDetails && parsedData.questionDetails.length > 0) {
          const newQuestions = parsedData.questionDetails.map(q => q.text);
          setQuestions(newQuestions);
          setSubtitle(newQuestions[0]);
        }
      } catch (e) {
        console.error("Error parsing stored interview data:", e);
      }
    } else {
      setSubtitle(questions[0]);
    }
    
    startWebcam();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startWebcam = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  const toggleMute = () => {
    if (stream) {
      stream.getAudioTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!isMuted);
    }
  };

  const toggleVideo = () => {
    if (stream) {
      stream.getVideoTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsVideoOn(!isVideoOn);
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSubtitle('');
      setTimeout(() => {
        setSubtitle(questions[currentQuestion + 1]);
      }, 300);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white font-sans overflow-hidden">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@300;400;600;700&family=DM+Sans:wght@400;500;700&display=swap');
        
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: 'DM Sans', sans-serif;
        }

        .interview-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          height: 100vh;
          position: relative;
        }

        .left-panel {
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          padding: 3rem;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          border-right: 1px solid rgba(255, 255, 255, 0.05);
          position: relative;
          overflow: hidden;
        }

        .left-panel::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -20%;
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
          animation: pulse 4s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 0.3; }
          50% { transform: scale(1.1); opacity: 0.5; }
        }

        .right-panel {
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          padding: 3rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          position: relative;
        }

        .right-panel::after {
          content: '';
          position: absolute;
          bottom: -30%;
          left: -20%;
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, rgba(16, 185, 129, 0.06) 0%, transparent 70%);
          animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.05); }
        }

        .webcam-container {
          width: 100%;
          max-width: 500px;
          aspect-ratio: 4/3;
          background: #000;
          border-radius: 24px;
          overflow: hidden;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
          border: 2px solid rgba(255, 255, 255, 0.1);
          position: relative;
          margin-bottom: 2rem;
        }

        .webcam-video {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .recording-indicator {
          position: absolute;
          top: 1.5rem;
          right: 1.5rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(10px);
          padding: 0.5rem 1rem;
          border-radius: 50px;
          font-size: 0.875rem;
          font-weight: 600;
        }

        .rec-dot {
          width: 8px;
          height: 8px;
          background: #ef4444;
          border-radius: 50%;
          animation: blink 1.5s infinite;
        }

        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }

        .controls {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }

        .control-btn {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          border: none;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }

        .control-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        }

        .control-btn:active {
          transform: translateY(0);
        }

        .control-btn.primary {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        .control-btn.danger {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }

        .control-btn.secondary {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
        }

        .interviewer-section {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          position: relative;
          z-index: 1;
        }

        .interviewer-header {
          margin-bottom: 3rem;
        }

        .interviewer-title {
          font-family: 'Crimson Pro', serif;
          font-size: 3.5rem;
          font-weight: 700;
          letter-spacing: -0.02em;
          margin-bottom: 0.5rem;
          background: linear-gradient(135deg, #ffffff 0%, #94a3b8 100%);
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: slideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .interviewer-subtitle {
          font-size: 1.125rem;
          color: #94a3b8;
          font-weight: 500;
          animation: slideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.1s backwards;
        }

        .avatar-container {
          width: 180px;
          height: 180px;
          margin: 0 auto 3rem;
          position: relative;
          animation: slideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s backwards;
        }

        .avatar-ring {
          position: absolute;
          inset: -10px;
          border-radius: 50%;
          background: linear-gradient(135deg, #3b82f6, #10b981);
          animation: rotate 3s linear infinite;
          opacity: 0.5;
        }

        @keyframes rotate {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .avatar-bg {
          position: absolute;
          inset: 0;
          border-radius: 50%;
          background: linear-gradient(135deg, #1e40af 0%, #059669 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 4rem;
          font-weight: 700;
          color: white;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .question-container {
          background: rgba(255, 255, 255, 0.05);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 20px;
          padding: 2.5rem;
          margin-bottom: 2rem;
          animation: slideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.3s backwards;
        }

        .question-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: #10b981;
          margin-bottom: 1rem;
        }

        .question-text {
          font-family: 'Crimson Pro', serif;
          font-size: 1.875rem;
          font-weight: 600;
          line-height: 1.4;
          color: #f1f5f9;
          animation: fadeInText 0.5s ease-out;
        }

        @keyframes fadeInText {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .progress-bar {
          height: 4px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          overflow: hidden;
          margin-bottom: 1rem;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #10b981);
          border-radius: 10px;
          transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .question-counter {
          font-size: 0.875rem;
          color: #64748b;
          text-align: center;
          margin-bottom: 2rem;
        }

        .next-btn {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          border: none;
          padding: 1rem 3rem;
          border-radius: 12px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.3);
          display: block;
          margin: 0 auto;
        }

        .next-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 15px 30px -5px rgba(16, 185, 129, 0.4);
        }

        .next-btn:active {
          transform: translateY(0);
        }


        @media (max-width: 1024px) {
          .interview-grid {
            grid-template-columns: 1fr;
            overflow-y: auto;
          }

          .left-panel, .right-panel {
            min-height: 50vh;
          }

          .interviewer-title {
            font-size: 2.5rem;
          }

          .question-text {
            font-size: 1.5rem;
          }
        }
      `}</style>

      <div className="interview-grid">
        {/* Left Panel - Interviewer */}
        <div className="left-panel">
          <div className="interviewer-section">
            <div className="interviewer-header">
              <h1 className="interviewer-title">AI Interviewer</h1>
              <p className="interviewer-subtitle">Sarah Mitchell, Senior Recruiter</p>
            </div>

            <div className="avatar-container">
              <div className="avatar-ring"></div>
              <div className="avatar-bg">SM</div>
            </div>

            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              ></div>
            </div>

            <div className="question-counter">
              Question {currentQuestion + 1} of {questions.length}
            </div>

            <div className="question-container">
              <div className="question-label">
                <MessageSquare size={16} />
                Current Question
              </div>
              <p className="question-text" key={currentQuestion}>{subtitle}</p>
            </div>

            {currentQuestion < questions.length - 1 && (
              <button className="next-btn" onClick={nextQuestion}>
                Next Question
              </button>
            )}
          </div>
        </div>

        {/* Right Panel - Candidate */}
        <div className="right-panel">
          <div className="webcam-container">
            <video 
              ref={videoRef}
              className="webcam-video"
              autoPlay 
              playsInline 
              muted
            />
            {isRecording && (
              <div className="recording-indicator">
                <div className="rec-dot"></div>
                <span>RECORDING</span>
              </div>
            )}
          </div>

          <div className="controls">
            <button 
              className={`control-btn ${isRecording ? 'danger' : 'primary'}`}
              onClick={toggleRecording}
              title={isRecording ? 'Stop Recording' : 'Start Recording'}
            >
              <Camera size={24} color="white" />
            </button>

            <button 
              className={`control-btn ${isMuted ? 'danger' : 'secondary'}`}
              onClick={toggleMute}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <MicOff size={24} color="white" /> : <Mic size={24} color="white" />}
            </button>

            <button 
              className={`control-btn ${!isVideoOn ? 'danger' : 'secondary'}`}
              onClick={toggleVideo}
              title={isVideoOn ? 'Turn Off Video' : 'Turn On Video'}
            >
              {isVideoOn ? <Video size={24} color="white" /> : <VideoOff size={24} color="white" />}
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
