import React, { useState } from 'react';
import { Link } from 'react-router-dom'; 
import './InterviewSetup.css';

function InterviewSetup() {
  const [formData, setFormData] = useState({
    companyName: '',
    jobDescription: ''
  });

  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.companyName.trim()) {
      newErrors.companyName = 'Company name is required';
    }
    
    if (!formData.jobDescription.trim()) {
      newErrors.jobDescription = 'Job description is required';
    } else if (formData.jobDescription.trim().length < 50) {
      newErrors.jobDescription = 'Please provide a more detailed job description (at least 50 characters)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleStartInterview = async () => {
  if (!validateForm()) {
    return;
  }

  // Prepare data to send to backend
  const interviewData = {
    companyName: formData.companyName.trim(),
    jobDescription: formData.jobDescription.trim(),
    timestamp: new Date().toISOString()
  };

  console.log('Interview data to be sent to backend:', interviewData);

  try {
    // Call your Flask backend
    const response = await fetch('http://localhost:5000/api/start-interview', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(interviewData)
    });

    const result = await response.json();

    if (response.ok && result.success) {
      console.log('Backend response:', result);
      console.log('Generated questions:', result.data.questions);
      
      // Store the questions and data for the interview
      localStorage.setItem('interviewData', JSON.stringify(result.data));
      
      // Navigate to interview page
      alert('Interview questions generated! Starting interview...');
      // window.location.href = '/interview'; // Uncomment when ready
    } else {
      console.error('Failed to start interview:', result.error);
      alert(`Failed to start interview: ${result.error}`);
    }
  } catch (error) {
    console.error('Error starting interview:', error);
    alert('Failed to connect to the server. Please try again.');
  }
  
};

  return (
    <div className="setup-container">
      <div className="setup-content">
        <div className="setup-header">
          <div className="logo">Get-into.tech</div>
          <h1>Let's Prepare Your Interview</h1>
          <p className="subtitle">Help us customize your AI interview experience</p>
        </div>

        <div className="setup-form">
          <div className="form-group">
            <label htmlFor="companyName">
              Company Name <span className="required">*</span>
            </label>
            <input
              type="text"
              id="companyName"
              name="companyName"
              value={formData.companyName}
              onChange={handleInputChange}
              placeholder="e.g., Google, Microsoft, Amazon"
              className={errors.companyName ? 'error' : ''}
            />
            {errors.companyName && (
              <span className="error-message">{errors.companyName}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="jobDescription">
              Job Description <span className="required">*</span>
            </label>
            <textarea
              id="jobDescription"
              name="jobDescription"
              value={formData.jobDescription}
              onChange={handleInputChange}
              placeholder="Paste the job description here or describe the role you're interviewing for. Include key responsibilities, required skills, and qualifications..."
              rows="10"
              className={errors.jobDescription ? 'error' : ''}
            />
            <div className="char-count">
              {formData.jobDescription.length} characters
            </div>
            {errors.jobDescription && (
              <span className="error-message">{errors.jobDescription}</span>
            )}
          </div>

          <div className="info-box">
            <div className="info-icon">💡</div>
            <div className="info-text">
              <strong>Tip:</strong> The more detailed your job description, the more tailored and relevant your AI interview questions will be!
            </div>
          </div>

          <Link to="/Interview-page"
            className="start-btn"
            onClick={handleStartInterview}
          >
            Start Interview
          </Link>
        </div>

        <div className="features-preview">
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <span>Tailored Questions</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">💬</span>
            <span>Voice-Based Interview</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <span>Instant Feedback</span>
          </div>
        </div>
      </div>

      <div className="setup-background">
        <div className="bg-circle circle-1"></div>
        <div className="bg-circle circle-2"></div>
        <div className="bg-circle circle-3"></div>
      </div>
    </div>
  );
}

export default InterviewSetup;