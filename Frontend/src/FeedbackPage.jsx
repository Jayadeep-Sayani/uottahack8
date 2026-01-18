import { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  AlertCircle, 
  TrendingUp, 
  Star, 
  Award,
  ThumbsUp,
  Target,
  Lightbulb,
  ArrowRight,
  Download,
  Sparkles,
  Zap,
  Heart
} from 'lucide-react';

export default function FeedbackPage() {
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        // TODO: Replace with your actual backend endpoint
        const response = await fetch('http://localhost:5000/api/get-feedback', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          }
        });

        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            setFeedback(result.data);
          }
        } else {
          console.error('Failed to fetch feedback');
        }
      } catch (error) {
        console.error('Error fetching feedback:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFeedback();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner"></div>
          <p className="text-lg text-slate-600 mt-4 font-medium">Analyzing your interview performance...</p>
          <p className="text-sm text-slate-500 mt-2">This may take a moment ✨</p>
        </div>
        <style>{`
          .loading-spinner {
            width: 60px;
            height: 60px;
            border: 5px solid #e0e7ff;
            border-top-color: #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 font-sans">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        
        body {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .feedback-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 3rem 2rem;
        }

        .header-section {
          text-align: center;
          margin-bottom: 4rem;
          padding: 2rem 0;
          position: relative;
        }


        .confetti-piece:nth-child(1) { left: 10%; animation-delay: 0s; background: #10b981; }
        .confetti-piece:nth-child(2) { left: 20%; animation-delay: 0.3s; background: #f59e0b; }
        .confetti-piece:nth-child(3) { left: 30%; animation-delay: 0.6s; background: #ef4444; }
        .confetti-piece:nth-child(4) { left: 40%; animation-delay: 0.9s; background: #3b82f6; }
        .confetti-piece:nth-child(5) { left: 50%; animation-delay: 1.2s; background: #8b5cf6; }
        .confetti-piece:nth-child(6) { left: 60%; animation-delay: 0.4s; background: #ec4899; }
        .confetti-piece:nth-child(7) { left: 70%; animation-delay: 0.7s; background: #14b8a6; }
        .confetti-piece:nth-child(8) { left: 80%; animation-delay: 1s; background: #f97316; }
        .confetti-piece:nth-child(9) { left: 90%; animation-delay: 0.2s; background: #06b6d4; }

    

        .completion-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.75rem;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          padding: 1rem 2rem;
          border-radius: 50px;
          font-weight: 700;
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          margin-bottom: 2rem;
          box-shadow: 0 20px 40px -10px rgba(16, 185, 129, 0.4);
          animation: bounce 2s ease-in-out infinite;
        }


        .main-title {
          font-size: 3.5rem;
          font-weight: 900;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
          -webkit-background-clip: text;
          background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 1rem;
          line-height: 1.2;
        }

        .subtitle {
          font-size: 1.25rem;
          color: #64748b;
          font-weight: 500;
        }

        .rating-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 2rem;
          padding: 4rem;
          color: white;
          text-align: center;
          margin-bottom: 4rem;
          box-shadow: 0 25px 50px -12px rgba(102, 126, 234, 0.5);
          position: relative;
          overflow: hidden;
        }

        .rating-card::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -20%;
          width: 500px;
          height: 500px;
          background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
          animation: float 8s ease-in-out infinite;
        }

        .rating-card::after {
          content: '';
          position: absolute;
          bottom: -30%;
          left: -20%;
          width: 400px;
          height: 400px;
          background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
          animation: float 6s ease-in-out infinite reverse;
        }

        .rating-icons {
          display: flex;
          justify-content: center;
          gap: 1rem;
          margin-bottom: 2rem;
          position: relative;
          z-index: 1;
        }

        .rating-icon {
          animation: sparkle 1.5s ease-in-out infinite;
        }

        .rating-icon:nth-child(2) { animation-delay: 0.2s; }
        .rating-icon:nth-child(3) { animation-delay: 0.4s; }


        .rating-label {
          font-size: 1.125rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.15em;
          margin-bottom: 1.5rem;
          opacity: 0.95;
          position: relative;
          z-index: 1;
        }

        .rating-text {
          font-size: 3.5rem;
          font-weight: 900;
          line-height: 1;
          margin-bottom: 1rem;
          position: relative;
          z-index: 1;
          text-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        .rating-description {
          font-size: 1.25rem;
          font-weight: 500;
          opacity: 0.95;
          position: relative;
          z-index: 1;
        }

        .content-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .section-card {
          background: white;
          border-radius: 2rem;
          padding: 2.5rem;
          box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.8);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .section-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 6px;
          background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        }

        .section-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
        }

        .section-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 2rem;
          padding-bottom: 1.5rem;
          border-bottom: 2px solid #f1f5f9;
        }

        .section-icon {
          width: 50px;
          height: 50px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .section-icon.success {
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
        }

        .section-icon.warning {
          background: linear-gradient(135deg, #f59e0b, #d97706);
          color: white;
        }

        .section-icon.info {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
        }

        .section-title {
          font-size: 1.75rem;
          font-weight: 800;
          color: #1a1a1a;
        }

        .strength-item {
          padding: 1.75rem;
          background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
          border-radius: 1.25rem;
          margin-bottom: 1.25rem;
          border-left: 5px solid #10b981;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .strength-item::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -20%;
          width: 150px;
          height: 150px;
          background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
          border-radius: 50%;
        }

        .strength-item:hover {
          transform: translateX(8px);
          box-shadow: 0 8px 20px -5px rgba(16, 185, 129, 0.3);
        }

        .strength-title {
          font-size: 1.125rem;
          font-weight: 700;
          color: #065f46;
          margin-bottom: 0.75rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .strength-description {
          font-size: 0.95rem;
          color: #047857;
          line-height: 1.7;
          position: relative;
          z-index: 1;
        }

        .weakness-item {
          padding: 1.75rem;
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border-radius: 1.25rem;
          margin-bottom: 1.25rem;
          border-left: 5px solid #f59e0b;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
        }

        .weakness-item::before {
          content: '';
          position: absolute;
          top: -50%;
          right: -20%;
          width: 150px;
          height: 150px;
          background: radial-gradient(circle, rgba(245, 158, 11, 0.1) 0%, transparent 70%);
          border-radius: 50%;
        }

        .weakness-item:hover {
          transform: translateX(8px);
          box-shadow: 0 8px 20px -5px rgba(245, 158, 11, 0.3);
        }

        .weakness-title {
          font-size: 1.125rem;
          font-weight: 700;
          color: #92400e;
          margin-bottom: 0.75rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .weakness-description {
          font-size: 0.95rem;
          color: #78350f;
          line-height: 1.7;
          position: relative;
          z-index: 1;
        }

        .full-width-card {
          grid-column: 1 / -1;
        }

        .improvement-category {
          margin-bottom: 2.5rem;
        }

        .category-title {
          font-size: 1.25rem;
          font-weight: 800;
          color: #1a1a1a;
          margin-bottom: 1.5rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: linear-gradient(135deg, #eff6ff, #dbeafe);
          border-radius: 1rem;
        }

        .suggestion-list {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .suggestion-item {
          display: flex;
          align-items: start;
          gap: 1rem;
          padding: 1.25rem 1.5rem;
          background: linear-gradient(135deg, #f8fafc, #f1f5f9);
          border-radius: 1rem;
          font-size: 0.95rem;
          color: #475569;
          line-height: 1.7;
          border: 2px solid transparent;
          transition: all 0.3s ease;
        }

        .suggestion-item:hover {
          border-color: #3b82f6;
          background: linear-gradient(135deg, #eff6ff, #dbeafe);
          transform: translateX(5px);
        }

        .suggestion-bullet {
          min-width: 32px;
          height: 32px;
          border-radius: 50%;
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 0.875rem;
          box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        }

        .actions-section {
          display: flex;
          gap: 1.5rem;
          justify-content: center;
          margin-top: 4rem;
        }

        .action-btn {
          padding: 1.25rem 2.5rem;
          border-radius: 1rem;
          font-weight: 700;
          font-size: 1.125rem;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          border: none;
        }

        .action-btn.primary {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
        }

        .action-btn.primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 35px -5px rgba(102, 126, 234, 0.5);
        }

        .action-btn.secondary {
          background: white;
          color: #667eea;
          border: 3px solid #667eea;
          box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.2);
        }

        .action-btn.secondary:hover {
          background: #eff6ff;
          transform: translateY(-3px);
          box-shadow: 0 15px 35px -5px rgba(102, 126, 234, 0.3);
        }

        @media (max-width: 1024px) {
          .content-grid {
            grid-template-columns: 1fr;
          }

          .main-title {
            font-size: 2.5rem;
          }

          .rating-text {
            font-size: 3rem;
          }
        }

        @media (max-width: 768px) {
          .feedback-container {
            padding: 1.5rem 1rem;
          }

          .main-title {
            font-size: 2rem;
          }

          .rating-card {
            padding: 2.5rem 1.5rem;
          }

          .actions-section {
            flex-direction: column;
          }

          .action-btn {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>

      <div className="feedback-container">
        {/* Header with Confetti */}
        <div className="header-section">
          <div className="confetti">
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
            <div className="confetti-piece"></div>
          </div>
          <div className="completion-badge">
            <Award size={20} />
            Interview Complete
          </div>
          <h1 className="main-title">Your Interview Feedback</h1>
          <p className="subtitle">Here's your personalized performance analysis</p>
        </div>

        {/* Strengths & Weaknesses */}
        <div className="content-grid">
          {/* Strengths */}
          <div className="section-card">
            <div className="section-header">
              <div className="section-icon success">
                <ThumbsUp size={24} />
              </div>
              <h2 className="section-title">Strengths</h2>
            </div>
            
            {feedback?.strengths?.map((strength, index) => (
              <div key={index} className="strength-item">
                <div className="strength-title">
                  <CheckCircle size={20} />
                  {strength.title}
                </div>
                <div className="strength-description">
                  {strength.description}
                </div>
              </div>
            ))}
          </div>

          {/* Weaknesses */}
          <div className="section-card">
            <div className="section-header">
              <div className="section-icon warning">
                <AlertCircle size={24} />
              </div>
              <h2 className="section-title">Areas to Work On</h2>
            </div>
            
            {feedback?.weaknesses?.map((weakness, index) => (
              <div key={index} className="weakness-item">
                <div className="weakness-title">
                  <Zap size={20} />
                  {weakness.title}
                </div>
                <div className="weakness-description">
                  {weakness.description}
                </div>
              </div>
            ))}
          </div>

          {/* Improvements - Full Width */}
          <div className="section-card full-width-card">
            <div className="section-header">
              <div className="section-icon info">
                <Lightbulb size={24} />
              </div>
              <h2 className="section-title">Actionable Improvements</h2>
            </div>
            
            {feedback?.improvements?.map((category, index) => (
              <div key={index} className="improvement-category">
                <div className="category-title">
                  <Target size={22} />
                  {category.category}
                </div>
                <ul className="suggestion-list">
                  {category.suggestions.map((suggestion, sIndex) => (
                    <li key={sIndex} className="suggestion-item">
                      <span className="suggestion-bullet">{sIndex + 1}</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="actions-section">
          <button className="action-btn secondary">
            <Download size={22} />
            Download Report
          </button>
          <button className="action-btn primary" onClick={() => window.location.href = '/'}>
            Practice Again
            <ArrowRight size={22} />
          </button>
        </div>
      </div>
    </div>
  );
}