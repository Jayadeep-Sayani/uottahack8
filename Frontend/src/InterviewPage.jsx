
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Mic, MicOff, Video, VideoOff, MessageSquare, Square, Circle, Loader2 } from 'lucide-react';
import logo from './assets/logo.png';

export default function InterviewPage() {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [subtitle, setSubtitle] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const [stream, setStream] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAISpeaking, setIsAISpeaking] = useState(false);

  useEffect(() => {
    startWebcam();
    clearRecordings();
    generateQuestions();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      // Cleanup audio on unmount
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const clearRecordings = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/clear-recordings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Recordings cleared:', result);
      } else {
        console.warn('Failed to clear recordings (this is okay)');
      }
    } catch (error) {
      console.warn('Error clearing recordings (this is okay):', error);
    }
  };

  const generateQuestions = async () => {
    const storedQuestions = localStorage.getItem('generatedQuestions');
    const interviewData = localStorage.getItem('interviewData');
    
    // Skip cached questions for now - always regenerate to ensure freshness
    // if (storedQuestions && interviewData) {
    //   try {
    //     const parsedQuestions = JSON.parse(storedQuestions);
    //     const questionsList = parsedQuestions.map(q => q.text);
    //     setQuestions(questionsList);
    //     setSubtitle(questionsList[0] || '');
    //     setLoading(false);
    //     return;
    //   } catch (e) {
    //     console.error('Error parsing stored questions:', e);
    //   }
    // }
    
    if (interviewData) {
      try {
        const data = JSON.parse(interviewData);
        console.log('Generating questions for:', data.companyName);
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
          console.log('Questions API response:', result);
          
          if (result.success && result.questions && result.questions.length > 0) {
            const questionsList = result.questions.map(q => q.text);
            console.log('Generated questions:', questionsList);
            setQuestions(questionsList);
            setSubtitle(questionsList[0] || '');
            localStorage.setItem('generatedQuestions', JSON.stringify(result.questions));
          } else {
            console.warn('No questions in response, using defaults');
            setQuestions([
              "Tell me about yourself and your background.",
              "What interests you most about this opportunity?"
            ]);
            setSubtitle("Tell me about yourself and your background.");
          }
        } else {
          const errorData = await response.json().catch(() => ({}));
          console.error('API error response:', response.status, errorData);
          setQuestions([
            "Tell me about yourself and your background.",
            "What interests you most about this opportunity?"
          ]);
          setSubtitle("Tell me about yourself and your background.");
        }
      } catch (error) {
        console.error('Error generating questions:', error);
        setQuestions([
          "Tell me about yourself and your background.",
          "What interests you most about this opportunity?"
        ]);
        setSubtitle("Tell me about yourself and your background.");
      } finally {
        setLoading(false);
      }
    } else {
      console.warn('No interview data found in localStorage');
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

  const startRecording = () => {
    if (!stream) {
      console.error("No media stream available");
      return;
    }

    recordedChunksRef.current = [];
    
    const options = { mimeType: 'video/webm;codecs=vp8,opus' };
    mediaRecorderRef.current = new MediaRecorder(stream, options);
    
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };
    
    mediaRecorderRef.current.onstop = async () => {
      const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
      await saveRecording(blob);
    };
    
    mediaRecorderRef.current.start();
    setIsRecording(true);
    console.log("Recording started for question", currentQuestion + 1);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
      setProcessingMessage('Preparing recording...');
      console.log("Recording stopped for question", currentQuestion + 1);
    }
  };

  const saveRecording = async (blob) => {
    try {
      setIsProcessing(true);
      setProcessingMessage('Saving recording...');
      
      const formData = new FormData();
      // Send as webm (browser format), backend will convert to mp4
      formData.append('audio', blob, `question_${currentQuestion + 1}.webm`);
      formData.append('questionNumber', currentQuestion + 1);
      
      const response = await fetch('http://localhost:5000/api/save-user-recording', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Recording saved:', result);
        setProcessingMessage('Recording saved! Moving to next question...');
        
        // Wait 2 seconds before moving to next question
        setTimeout(() => {
          setIsProcessing(false);
          setProcessingMessage('');
          moveToNextQuestion();
        }, 2000);
      } else {
        console.error('Failed to save recording');
        setIsProcessing(false);
        setProcessingMessage('');
        moveToNextQuestion();
      }
    } catch (error) {
      console.error('Error saving recording:', error);
      setIsProcessing(false);
      setProcessingMessage('');
      moveToNextQuestion();
    }
  };

  const moveToNextQuestion = async () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSubtitle('');
      setTimeout(() => {
        setSubtitle(questions[currentQuestion + 1]);
      }, 300);
    } else {
      // Interview finished - analyze all recordings
      setIsAnalyzing(true);
      setIsProcessing(true);
      setProcessingMessage('Analyzing recordings and generating feedback...');
      
      try {
        // Get interview metadata from localStorage
        const interviewData = localStorage.getItem('interviewData');
        const storedQuestions = localStorage.getItem('generatedQuestions');
        
        const requestBody = {};
        
        if (interviewData) {
          try {
            const data = JSON.parse(interviewData);
            requestBody.companyName = data.companyName || '';
            requestBody.jobDescription = data.jobDescription || '';
          } catch (e) {
            console.error('Error parsing interview data:', e);
          }
        }
        
        if (storedQuestions) {
          try {
            requestBody.questions = JSON.parse(storedQuestions);
          } catch (e) {
            console.error('Error parsing questions:', e);
          }
        }
        
        const response = await fetch('http://localhost:5000/api/analyze-recordings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log('Analysis complete:', result);
          
          // Hide loading overlay - overall feedback is already generated on backend
          setIsAnalyzing(false);
          setIsProcessing(false);
          setProcessingMessage('');
          
          // DISABLED: TTS for final recommendation to save ElevenLabs credits
          // Navigate directly to feedback page
          // try {
          //   // Fetch overall feedback
          //   const feedbackResponse = await fetch('http://localhost:5000/api/get-overall-feedback');
          //   if (feedbackResponse.ok) {
          //     const overallFeedback = await feedbackResponse.json();
          //     const finalRecommendation = overallFeedback.final_recommendation || 'Thank you for completing the interview.';
          //     
          //     // Speak the final recommendation
          //     await speakText(finalRecommendation);
          //     
          //     // Wait a moment, then speak ending message
          //     await new Promise(resolve => setTimeout(resolve, 500));
          //     await speakText('This ends the interview.');
          //   }
          // } catch (error) {
          //   console.error('Error fetching overall feedback or speaking:', error);
          // }
          
          // Navigate to feedback page
          navigate('/feedback');
        } else {
          const error = await response.json();
          console.error('Analysis failed:', error);
          setIsAnalyzing(false);
          setIsProcessing(false);
          setProcessingMessage('');
          alert('Interview completed! However, analysis encountered an error. Please check the console.');
        }
      } catch (error) {
        console.error('Error analyzing recordings:', error);
        setIsAnalyzing(false);
        setIsProcessing(false);
        setProcessingMessage('');
        alert('Interview completed! However, analysis encountered an error. Please check the console.');
      }
    }
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

  const audioRef = useRef(null);

  // Function to speak text using ElevenLabs TTS via backend API
  const speakText = async (text) => {
    return new Promise((resolve, reject) => {
      try {
        // Stop any currently playing audio
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        }

        // Call the backend TTS API
        fetch('http://localhost:5000/api/text-to-speech', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text: text })
        })
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error('Failed to generate TTS audio');
          }
        })
        .then(result => {
          if (result.success && result.audioUrl) {
            // Create audio element and play
            const audio = new Audio(`http://localhost:5000${result.audioUrl}`);
            audioRef.current = audio;
            
            // Set speaking state when audio starts
            audio.onplay = () => setIsAISpeaking(true);
            
            // Resolve when audio finishes playing
            audio.onended = () => {
              setIsAISpeaking(false);
              resolve();
            };
            
            audio.onerror = (err) => {
              console.error('Error playing audio:', err);
              setIsAISpeaking(false);
              reject(err);
            };
            
            audio.play().catch(err => {
              console.error('Error playing audio:', err);
              setIsAISpeaking(false);
              reject(err);
            });
          } else {
            console.warn('TTS API returned but no audio URL provided');
            resolve(); // Resolve anyway to continue
          }
        })
        .catch(error => {
          console.error('Error calling TTS API:', error);
          reject(error);
        });
      } catch (error) {
        console.error('Error in speakText:', error);
        reject(error);
      }
    });
  };

  // Effect to speak question when subtitle changes
  // DISABLED: TTS temporarily disabled to save ElevenLabs credits
  /*
  useEffect(() => {
    if (subtitle && !loading) {
      // Wait a bit for the animation, then speak
      const timer = setTimeout(() => {
        speakText(subtitle);
      }, 500);
      
      return () => {
        clearTimeout(timer);
        // Stop audio when component unmounts or subtitle changes
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        }
      };
    }
  }, [subtitle, loading]);
  */

  const nextQuestion = () => {
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsAISpeaking(false);
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSubtitle('');
      setTimeout(() => {
        setSubtitle(questions[currentQuestion + 1]);
      }, 300);
    }
  };

  return (
    <div className="font-sans" style={{ height: '100vh', overflow: 'hidden' }}>
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
          width: 100%;
          height: 100vh;
          display: flex;
          flex-direction: column;
          background: #f8fafc;
          overflow: hidden;
        }

        .interview-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 2rem;
          background: white;
          border-bottom: 1px solid #e2e8f0;
          z-index: 10;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 1.5rem;
          font-weight: 800;
          color: #2563eb;
        }

        .logo img {
          height: 2rem;
          width: auto;
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
          background: linear-gradient(90deg, #7362f3, #8b7af5);
          border-radius: 10px;
          transition: width 0.4s ease;
        }

        .interview-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          height: calc(100vh - 80px);
          position: relative;
          gap: 0;
        }

        .left-section {
          background: white;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          padding: 3rem;
          position: relative;
          overflow: hidden;
          border-right: 2px solid #e2e8f0;
        }

        .interviewer-card {
          background: transparent;
          display: flex;
          flex-direction: column;
          height: 100%;
          width: 100%;
          justify-content: center;
          align-items: center;
        }

        .ai-profile-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 80%;
          width: 100%;
          margin: 0 auto;
        }

        .ai-profile-container.speaking {
          border: 3px solid #10b981;
          border-radius: 1rem;
          box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
          animation: pulse-border 2s ease-in-out infinite;
        }

        @keyframes pulse-border {
          0%, 100% {
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
          }
          50% {
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.6);
          }
        }

        .avatar-circle {
          width: 200px;
          height: 200px;
          border-radius: 50%;
          background: linear-gradient(135deg, #7362f3 0%, #8b7af5 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 4rem;
          font-weight: 700;
          color: white;
          box-shadow: 0 20px 40px -10px rgba(37, 99, 235, 0.3);
          margin-bottom: 1.5rem;
        }

        .interviewer-name {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 0.25rem;
          text-align: center;
        }

        .interviewer-role {
          font-size: 0.95rem;
          color: #64748b;
          font-weight: 500;
          text-align: center;
        }

        .question-card {
          background: transparent;
          padding: 0;
          border: none;
          box-shadow: none;
          color: #1a1a1a;
          position: absolute;
          top: 2rem;
          left: 50%;
          width: 85%;
          max-width: 700px;
          transform: translateX(-50%);
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
          align-items: center;
          text-align: center;
          pointer-events: none;
        }

        .question-card:hover {
          transform: none;
          background: transparent;
          border: none;
          box-shadow: none;
        }


        .question-label {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          color: #64748b;
          padding: 0;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          margin-bottom: 0.5rem;
        }

        .question-text {
          font-size: 0.875rem;
          font-weight: 500;
          line-height: 1.5;
          position: relative;
          z-index: 1;
          color: #475569;
          margin: 0;
        }

        .processing-message {
          background: transparent;
          padding: 0;
          border: none;
          border-radius: 0;
          margin-top: 0.75rem;
          text-align: center;
          font-weight: 500;
          position: relative;
          z-index: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          color: #64748b;
        }

        .spinning {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .loading-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 9999;
          flex-direction: column;
          gap: 1.5rem;
        }

        .loading-overlay-content {
          background: white;
          border-radius: 1.5rem;
          padding: 3rem;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          text-align: center;
          max-width: 400px;
        }

        .loading-overlay-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 0.5rem;
        }

        .loading-overlay-message {
          font-size: 1rem;
          color: #64748b;
          margin-top: 1rem;
        }

        .loading-spinner {
          width: 48px;
          height: 48px;
          border: 4px solid #e5e7eb;
          border-top-color: #7362f3;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto;
        }

        .right-section {
          background: #1e293b;
          display: flex;
          flex-direction: column;
          position: relative;
        }

        .video-card {
          background: transparent;
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .video-label-text {
          position: absolute;
          top: 1rem;
          left: 1rem;
          font-size: 0.875rem;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.9);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          z-index: 5;
          background: rgba(0, 0, 0, 0.6);
          padding: 0.5rem 1rem;
          border-radius: 50px;
          backdrop-filter: blur(10px);
        }

        .webcam-container {
          width: 100%;
          height: 100%;
          background: #000;
          overflow: hidden;
          position: relative;
        }

        .webcam-video {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transform: scaleX(-1);
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
          position: fixed;
          bottom: 5rem;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 1rem;
          justify-content: center;
          z-index: 1000;
        }

        .control-button {
          width: 80px;
          height: 80px;
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

        .control-button:hover:not(:disabled) {
          transform: translateY(-4px) scale(1.05);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        }

        .control-button:active {
          transform: translateY(-2px) scale(1.02);
        }

        .control-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .control-button.record-start {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }

        .control-button.record-stop {
          background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
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
          color: #7362f3;
          font-weight: 700;
          font-size: 0.75rem;
          margin-top: 0.125rem;
        }

        @media (max-width: 1280px) {
          .interview-grid {
            grid-template-columns: 1fr;
          }

          .left-section {
            height: 40vh;
          }

          .right-section {
            height: 60vh;
          }

          .question-text {
            font-size: 1.5rem;
          }
        }

        @media (max-width: 768px) {
          .interview-header {
            padding: 1rem;
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

          .left-section {
            padding: 2rem 1.5rem;
          }

          .interviewer-header-section {
            flex-direction: column;
            text-align: center;
            gap: 1rem;
          }

          .question-text {
            font-size: 1.25rem;
          }

          .question-card {
            padding: 1.5rem;
          }

          .controls-section {
            bottom: 1rem;
            padding: 0.75rem 1rem;
            gap: 0.75rem;
          }

          .control-button {
            width: 48px;
            height: 48px;
          }
        }
      `}</style>

      {/* Loading screen while generating questions */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-overlay-content">
            <div className="loading-spinner"></div>
            <h3 className="loading-overlay-title">Preparing Your Interview</h3>
            <p className="loading-overlay-message">
              Generating personalized interview questions based on your job description. This may take a few seconds...
            </p>
          </div>
        </div>
      )}

      {/* Only show interview interface when questions are loaded */}
      {!loading && questions.length > 0 ? (
        <>
          {isAnalyzing && (
            <div className="loading-overlay">
              <div className="loading-overlay-content">
                <div className="loading-spinner"></div>
                <h3 className="loading-overlay-title">Analyzing Interview</h3>
                <p className="loading-overlay-message">
                  Processing your recordings and generating feedback. This may take a minute...
                </p>
              </div>
            </div>
          )}

          <div className="interview-container">
        {/* Header */}
        <div className="interview-header">
          <div className="logo">
            <img src={logo} alt="Logo" />
            <span>Get-into.tech</span>
          </div>
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
          {/* Left Section - AI Interviewer */}
          <div className="left-section">
            <div className="interviewer-card">
              <div className={`ai-profile-container ${isAISpeaking ? 'speaking' : ''}`}>
                <div className="avatar-circle">AI</div>
                <h2 className="interviewer-name">AI Interviewer</h2>
                <p className="interviewer-role">Powered by Get-into.tech</p>
              </div>

              {/* Current Question - Positioned near bottom */}
              <div className="question-card">
                <span className="question-label">
                  <MessageSquare size={14} />
                  Question {currentQuestion + 1}
                </span>
                <p className="question-text" key={currentQuestion}>
                  {subtitle}
                </p>
                
                {isProcessing && processingMessage && (
                  <div className="processing-message">
                    <Loader2 size={16} className="spinning" />
                    <span>{processingMessage}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Section - User Video */}
          <div className="right-section">
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

            </div>
          </div>
        </div>

        {/* Controls - Centered horizontally across entire screen */}
        <div className="controls-section">
          {!isRecording ? (
            <button 
              className="control-button record-start"
              onClick={startRecording}
              disabled={isProcessing || loading}
              title="Start Recording"
            >
              <Circle size={36} color="white" fill="white" />
            </button>
          ) : (
            <button 
              className="control-button record-stop"
              onClick={stopRecording}
              title="Stop Recording"
            >
              <Square size={36} color="white" fill="white" />
            </button>
          )}
        </div>
        </div>
        </>
      ) : !loading && questions.length === 0 ? (
        <div className="loading-overlay">
          <div className="loading-overlay-content">
            <h3 className="loading-overlay-title">Unable to Load Questions</h3>
            <p className="loading-overlay-message">
              There was an issue generating questions. Please go back and try again.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
} 