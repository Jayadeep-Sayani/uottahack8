import React, { useState } from 'react';
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
      const response = await fetch('/api/start-interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(interviewData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Backend response:', result);
        
        // Store in localStorage as backup
        localStorage.setItem('interviewData', JSON.stringify(interviewData));
        
        // Navigate to interview page or next step
        // window.location.href = '/interview'; // Uncomment when ready
        alert('Interview setup complete! Starting interview...');
      } else {
        console.error('Failed to start interview');
        alert('Failed to start interview. Please try again.');
      }
    } catch (error) {
      console.error('Error starting interview:', error);
      
      // Fallback: save to localStorage if backend fails
      localStorage.setItem('interviewData', JSON.stringify(interviewData));
      alert('Data saved locally. Starting interview...');
      
      // You can still proceed to interview page
      // window.location.href = '/interview';
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

          <button 
            className="start-btn"
            onClick={handleStartInterview}
          >
            Start Interview
          </button>
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