import React from 'react';
import './App.css'; // Import the CSS file
import { useState, useEffect } from 'react'; 
import { BrowserRouter, Route, Routes, Link } from 'react-router-dom';
import InterviewSetup from './InterviewSetup.jsx'
import InterviewPage from './InterviewPage.jsx'


function LoadingPage() {
  return (
    <div className="loading-container">
      <div className="loading-content">
        <div className="logo-animation">
          <h1 className="loading-logo">Get-into.tech</h1>
          <div className="loading-tagline">Ace Your Interview with AI</div>
        </div>
        
        <div className="loader">
          <div className="loader-bar"></div>
        </div>
        
        <div className="loading-text">Preparing your experience...</div>
      </div>
      
      <div className="loading-background">
        <div className="circle circle-1"></div>
        <div className="circle circle-2"></div>
        <div className="circle circle-3"></div>
      </div>
    </div>
  );
}

function LandingPage(){
  return (
    <div className="App">
      <nav>
        <div className="nav-container">
          <div className="logo">Get-into.tech</div>
          <div className="nav-links">
            <a href="#practice">Practice</a>
            <a href="#features">Features</a>
            <a href="#pricing">Pricing</a>
            <a href="#contact">Contact</a>
            <button className="practice-btn">Practice Interview</button>
          </div>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <h1>
              Voice-Based<br />
              Interactive AI<br />
              Interviewer
            </h1>
            <div className="promo-badge">
              🎉 Try 3 AI Interview sessions for FREE! 🎉
            </div>
            <Link to="/Job-Info" className="cta-btn">Practice Interview</Link>
           
            <div className="trust-section">
              <p>Trusted by Students and Professionals from</p>
              <div className="trust-logos">
                <span className="trust-logo">Yale Alumni</span>
                <span className="trust-logo">MIT</span>
                <span className="trust-logo">Stanford</span>
                <span className="trust-logo">Harvard</span>
              </div>
            </div>
          </div>


          <div className="hero-image">
            <div className="mockup-container">
              <div className="mockup-header">
                <span className="mockup-logo">Get-into.tech</span>
                <div className="mockup-nav">
                  <span>Practice</span>
                  <span>My Interviews</span>
                  <span>Questions</span>
                </div>
              </div>
              <div className="mockup-content">
                <div className="interview-display">
                  <div className="interviewer-video">
                    <div className="video-placeholder">👩‍💼</div>
                    <span className="video-label">AI Interviewer</span>
                  </div>
                  <div className="candidate-video">
                    <div className="video-placeholder">👨‍💻</div>
                    <span className="video-label">You</span>
                  </div>
                </div>
                <div className="question-box">
                  <p>Hello! Thank you for joining this interview. We'll start with some sort questions to get to know you better...</p>
                </div>
                <div className="controls">
                  <button className="control-btn mute">Mute</button>
                  <button className="control-btn">Respond</button>
                  <button className="control-btn next">Next Q</button>
                  <button className="control-btn end">End</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section> 
      <section className="features" id="features">
        <h2>Why Choose Get-into.tech?</h2>
       
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Realistic Practice</h3>
            <p>
              AI-powered interviews that simulate real scenarios with
              industry-specific questions
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💡</div>
            <h3>Instant Feedback</h3>
            <p>
              Get detailed analysis on your answers, body language, and
              communication skills
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Personalized Experience</h3>
            <p>
              Tailored questions and feedback based on your industry, role,
              and skill level
            </p>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <h2>How It Works</h2>
       
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h4>Choose Role</h4>
            <p>Select your target position</p>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <h4>Practice</h4>
            <p>Answer AI questions</p>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <h4>Get Feedback</h4>
            <p>Receive detailed insights</p>
          </div>

          <div className="step">
            <div className="step-number">4</div>
            <h4>Land the Job</h4>
            <p>Ace your interview</p>
          </div>
        </div>
      </section>
      <section className="testimonial">
        <div className="testimonial-card">
          <p>
            "Get-into.tech helped me land my dream job at FaceAppGoogflix.
            The AI feedback was incredibly accurate and helpful!"
          </p>
          <div className="testimonial-author">- Jason Ye, Software Engineer</div>
        </div>
      </section>
      <section className="final-cta">
        <h2>Ready to Ace Your Interview?</h2>
        <p>Join thousands of candidates who've landed their dream jobs</p>
        <button className="btn-large">Get Started for Free</button>
      </section>
      <footer>
        <p>© 2026 Get-into.tech. All rights reserved.</p>
      </footer>
    </div>
  )
}

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return <LoadingPage />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/Job-Info" element={<InterviewSetup />} />
        <Route path="/interview" element={<InterviewPage />} />
      </Routes>
    </BrowserRouter>
  );
}


export default App;
