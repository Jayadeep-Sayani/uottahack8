import { useState, useRef, useEffect } from 'react';
import { Camera, Mic, MicOff, Video, VideoOff, MessageSquare, ArrowRight } from 'lucide-react';

export default function InterviewPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [subtitle, setSubtitle] = useState('');
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    startWebcam();
    generateQuestions();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const generateQuestions = async () => {
    // Check if questions already exist in localStorage
    const storedQuestions = localStorage.getItem('generatedQuestions');
    const interviewData = localStorage.getItem('interviewData');
    
    if (storedQuestions && interviewData) {
      try {
        const parsedQuestions = JSON.parse(storedQuestions);
        const questionsList = parsedQuestions.map(q => q.text);
        setQuestions(questionsList);
        setSubtitle(questionsList[0] || '');
        setLoading(false);
        return;
      } catch (e) {
        console.error('Error parsing stored questions:', e);
      }
    }
    
    // If no questions in localStorage, generate them
    if (interviewData) {
      try {
        const data = JSON.parse(interviewData);
        setLoading(true);
        
        const response = await fetch('http://localhost:5000/api/start-interview', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            companyName: data.companyName,
            jobDescription: data.jobDescription
          })
        });

        if (response.ok) {
          const result = await response.json();
          
          // Print questions to console
          if (result.questions && result.questions.length > 0) {
            console.log('\n=== Generated Interview Questions ===');
            result.questions.forEach(q => {
              console.log(`\nQuestion ${q.number} (${q.type}):`);
              console.log(q.text);
            });
            console.log('\n=====================================\n');
          }
          
          const questionsList = result.questions.map(q => q.text);
          setQuestions(questionsList);
          setSubtitle(questionsList[0] || '');
          
          // Store in localStorage
          localStorage.setItem('generatedQuestions', JSON.stringify(result.questions || []));
        } else {
          console.error('Failed to generate questions');
          // Fallback to default questions
          setQuestions([
            "Tell me about yourself and your background.",
            "What interests you most about this opportunity?"
          ]);
          setSubtitle("Tell me about yourself and your background.");
        }
      } catch (error) {
        console.error('Error generating questions:', error);
        // Fallback to default questions
        setQuestions([
          "Tell me about yourself and your background.",
          "What interests you most about this opportunity?"
        ]);
        setSubtitle("Tell me about yourself and your background.");
      } finally {
        setLoading(false);
      }
    } else {
      // No interview data, use default questions
      setQuestions([
        "Tell me about yourself and your background.",
        "What interests you most about this opportunity?"
      ]);
      setSubtitle("Tell me about yourself and your background.");
      setLoading(false);
    }
  };

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 font-sans">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .interview-container {
          max-width: 1600px;
          margin: 0 auto;
          padding: 2rem;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .interview-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1.5rem;
          border-bottom: 1px solid #e2e8f0;
        }

        .logo {
          font-size: 1.5rem;
          font-weight: 800;
          color: #2563eb;
        }

        .interview-info {
          display: flex;
          align-items: center;
          gap: 2rem;
        }

        .question-progress {
          font-size: 0.9rem;
          color: #64748b;
          font-weight: 500;
        }

        .progress-bar-container {
          width: 200px;
          height: 6px;
          background: #e2e8f0;
          border-radius: 10px;
          overflow: hidden;
        }

        .progress-bar-fill {
          height: 100%;
          background: linear-gradient(90deg, #2563eb, #3b82f6);
          border-radius: 10px;
          transition: width 0.4s ease;
        }

        .interview-grid {
          display: grid;
          grid-template-columns: 1.2fr 1fr;
          gap: 2rem;
          flex: 1;
          align-items: start;
        }

        .left-section {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .interviewer-card {
          background: white;
          border-radius: 1.5rem;
          padding: 2.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
          border: 1px solid #f1f5f9;
        }

        .interviewer-header-section {
          display: flex;
          align-items: center;
          gap: 1.5rem;
          margin-bottom: 2rem;
          padding-bottom: 2rem;
          border-bottom: 1px solid #f1f5f9;
        }

        .avatar-circle {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          font-weight: 700;
          color: white;
          box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
        }

        .interviewer-info {
          flex: 1;
        }

        .interviewer-name {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 0.25rem;
        }

        .interviewer-role {
          font-size: 0.95rem;
          color: #64748b;
          font-weight: 500;
        }

        .question-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 1.5rem;
          padding: 2.5rem;
          color: white;
          position: relative;
          overflow: hidden;
          box-shadow: 0 20px 40px -10px rgba(102, 126, 234, 0.3);
        }

        .question-card::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -20%;
          width: 300px;
          height: 300px;
          background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
          animation: floatBackground 6s ease-in-out infinite;
        }

        @keyframes floatBackground {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(-20px, 20px); }
        }

        .question-label {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
          padding: 0.5rem 1rem;
          border-radius: 50px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 1.5rem;
        }

        .question-text {
          font-size: 1.75rem;
          font-weight: 600;
          line-height: 1.4;
          position: relative;
          z-index: 1;
          animation: fadeInUp 0.5s ease;
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .next-button {
          background: white;
          color: #667eea;
          border: none;
          padding: 1rem 2rem;
          border-radius: 0.75rem;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 2rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .next-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.15);
        }

        .next-button:active {
          transform: translateY(0);
        }

        .right-section {
          display: flex;
          flex-direction: column;
          gap: 2rem;
          position: sticky;
          top: 2rem;
        }

        .video-card {
          background: white;
          border-radius: 1.5rem;
          padding: 1.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
          border: 1px solid #f1f5f9;
        }

        .video-label-text {
          font-size: 0.875rem;
          font-weight: 600;
          color: #64748b;
          margin-bottom: 1rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .webcam-container {
          width: 100%;
          aspect-ratio: 4/3;
          background: #000;
          border-radius: 1rem;
          overflow: hidden;
          position: relative;
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
        }

        .webcam-video {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .recording-badge {
          position: absolute;
          top: 1rem;
          right: 1rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(0, 0, 0, 0.8);
          backdrop-filter: blur(10px);
          padding: 0.5rem 1rem;
          border-radius: 50px;
          font-size: 0.75rem;
          font-weight: 700;
          color: white;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .rec-dot {
          width: 8px;
          height: 8px;
          background: #ef4444;
          border-radius: 50%;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.9); }
        }

        .controls-section {
          display: flex;
          gap: 1rem;
          justify-content: center;
          margin-top: 1rem;
        }

        .control-button {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          border: none;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          position: relative;
        }

        .control-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.15);
        }

        .control-button:active {
          transform: translateY(0);
        }

        .control-button.primary {
          background: #2563eb;
        }

        .control-button.danger {
          background: #ef4444;
        }

        .control-button.secondary {
          background: #f1f5f9;
        }

        .control-button.secondary svg {
          color: #64748b;
        }

        .control-button.muted {
          background: #ef4444;
        }

        .control-button.muted svg {
          color: white;
        }

        .tips-card {
          background: white;
          border-radius: 1.5rem;
          padding: 2rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
          border: 1px solid #f1f5f9;
        }

        .tips-title {
          font-size: 1rem;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 1rem;
        }

        .tips-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .tip-item {
          display: flex;
          align-items: start;
          gap: 0.75rem;
          font-size: 0.875rem;
          color: #64748b;
          line-height: 1.6;
        }

        .tip-icon {
          min-width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #dbeafe;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #2563eb;
          font-weight: 700;
          font-size: 0.75rem;
          margin-top: 0.125rem;
        }

        @media (max-width: 1280px) {
          .interview-grid {
            grid-template-columns: 1fr;
          }

          .right-section {
            position: relative;
            top: 0;
          }

          .question-text {
            font-size: 1.5rem;
          }
        }

        @media (max-width: 768px) {
          .interview-container {
            padding: 1rem;
          }

          .interview-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .interview-info {
            width: 100%;
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
          }

          .interviewer-header-section {
            flex-direction: column;
            text-align: center;
          }

          .question-text {
            font-size: 1.25rem;
          }
        }
      `}</style>

      <div className="interview-container">
        {/* Header */}
        <div className="interview-header">
          <div className="logo">InterviewAI</div>
          <div className="interview-info">
            <div className="question-progress">
              Question {currentQuestion + 1} of {questions.length}
            </div>
            <div className="progress-bar-container">
              <div 
                className="progress-bar-fill"
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="interview-grid">
          {/* Left Section */}
          <div className="left-section">
            {/* Interviewer Info */}
            <div className="interviewer-card">
              <div className="interviewer-header-section">
                <div className="avatar-circle">AI</div>
                <div className="interviewer-info">
                  <h2 className="interviewer-name">AI Interviewer</h2>
                  <p className="interviewer-role">Powered by InterviewAI</p>
                </div>
              </div>

              {/* Current Question */}
              <div className="question-card">
                <span className="question-label">
                  <MessageSquare size={14} />
                  Question {currentQuestion + 1}
                </span>
                <p className="question-text" key={currentQuestion}>
                  {subtitle}
                </p>
                {!loading && questions.length > 0 && currentQuestion < questions.length - 1 && (
                  <button className="next-button" onClick={nextQuestion}>
                    Next Question
                    <ArrowRight size={18} />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Right Section */}
          <div className="right-section">
            {/* Video Feed */}
            <div className="video-card">
              <div className="video-label-text">Your Video</div>
              <div className="webcam-container">
                <video 
                  ref={videoRef}
                  className="webcam-video"
                  autoPlay 
                  playsInline 
                  muted
                />
                {isRecording && (
                  <div className="recording-badge">
                    <div className="rec-dot"></div>
                    Recording
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="controls-section">
                <button 
                  className={`control-button ${isRecording ? 'danger' : 'primary'}`}
                  onClick={toggleRecording}
                  title={isRecording ? 'Stop Recording' : 'Start Recording'}
                >
                  <Camera size={22} color="white" />
                </button>

                <button 
                  className={`control-button ${isMuted ? 'muted' : 'secondary'}`}
                  onClick={toggleMute}
                  title={isMuted ? 'Unmute' : 'Mute'}
                >
                  {isMuted ? <MicOff size={22} /> : <Mic size={22} />}
                </button>

                <button 
                  className={`control-button ${!isVideoOn ? 'danger' : 'secondary'}`}
                  onClick={toggleVideo}
                  title={isVideoOn ? 'Turn Off Video' : 'Turn On Video'}
                >
                  {isVideoOn ? <Video size={22} /> : <VideoOff size={22} color="white" />}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}