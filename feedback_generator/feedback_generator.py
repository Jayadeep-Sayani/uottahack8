"""
Module to generate personalized interview feedback using Google Gemini API.
Takes company name, job description, question text, and all 4 analysis JSON files
to generate 4 bullet point feedback in JSON format.
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()


class InterviewFeedbackGenerator:
    """
    A class to generate interview feedback based on speech, body language, 
    eye contact, and confidence analysis results.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the generator with Gemini API.
        
        Args:
            api_key: Google Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key not provided and GEMINI_API_KEY environment variable not set. "
                "Please set your Gemini API key."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    def generate_feedback(
        self,
        company_name: str,
        job_description: str,
        question_text: str,
        speech_confidence_json_path: str,
        body_language_json_path: str,
        eye_contact_json_path: str,
        modulation_json_path: str
    ) -> Dict[str, List[str]]:
        """
        Generate feedback based on all analysis results.
        
        Args:
            company_name: Name of the company
            job_description: Description of the job position
            question_text: The interview question that was answered
            speech_confidence_json_path: Path to speech confidence analysis JSON
            body_language_json_path: Path to body language analysis JSON
            eye_contact_json_path: Path to eye contact analysis JSON
            modulation_json_path: Path to speech modulation analysis JSON
        
        Returns:
            A dictionary with feedback containing 4 bullet points in JSON format
        """
        # Load all JSON files
        speech_data = self._load_json(speech_confidence_json_path)
        body_language_data = self._load_json(body_language_json_path)
        eye_contact_data = self._load_json(eye_contact_json_path)
        modulation_data = self._load_json(modulation_json_path)
        
        # Create prompt with all the data
        prompt = self._create_prompt(
            company_name=company_name,
            job_description=job_description,
            question_text=question_text,
            speech_data=speech_data,
            body_language_data=body_language_data,
            eye_contact_data=eye_contact_data,
            modulation_data=modulation_data
        )
        
        # Generate feedback using Gemini
        response = self.model.generate_content(prompt)
        feedback = self._parse_response(response.text)
        
        return feedback
    
    def _load_json(self, json_path: str) -> Dict:
        """Load JSON file from path."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_prompt(
        self,
        company_name: str,
        job_description: str,
        question_text: str,
        speech_data: Dict,
        body_language_data: Dict,
        eye_contact_data: Dict,
        modulation_data: Dict
    ) -> str:
        """
        Create the prompt for Gemini API with all analysis data.
        """
        # Extract transcript from modulation data
        candidate_answer = modulation_data.get("transcript", "No transcript available")
        
        prompt = f"""You are an expert interview coach providing constructive, human feedback for an interview candidate. Your role is to evaluate both the CONTENT of their answer and how they DELIVERED it.

IMPORTANT: Focus on analyzing what the candidate ACTUALLY SAID and whether it addresses the question. Do NOT simply restate statistics or scores. Provide natural, conversational feedback that a human coach would give.

Company: {company_name}
Job Description: {job_description}

Interview Question:
{question_text}

Candidate's Actual Answer (Transcript):
{candidate_answer}

Performance Metrics (for context - use these insights but don't just repeat them):

Speech Confidence: {speech_data.get('confidence_score', 'N/A')} - {speech_data.get('assessment', 'N/A')}
{speech_data.get('interpretation', '')}

Body Language: {body_language_data.get('overall_score', 'N/A')} - {body_language_data.get('assessment', 'N/A')}
{body_language_data.get('interpretation', '')}

Eye Contact: {eye_contact_data.get('overall_score', 'N/A')} - {eye_contact_data.get('assessment', 'N/A')}
{eye_contact_data.get('interpretation', '')}

Speech Patterns: {modulation_data.get('summary', {})}

Provide exactly 4 bullet points of constructive feedback. Your feedback should:

1. **Analyze the ANSWER CONTENT first**: Does the answer actually address the question? Is it accurate, relevant, and appropriate for this role at {company_name}? What's missing or could be improved in terms of what they said?

2. **Evaluate ANSWER STRUCTURE**: Is the answer well-organized? Does it tell a clear story or make a clear point? Does it connect to the job requirements?

3. **Assess DELIVERY** (referencing metrics naturally): How did they present themselves? Use insights from the metrics to give specific, actionable advice about delivery, but frame it as a human coach would - not as statistics.

4. **Provide SPECIFIC, ACTIONABLE IMPROVEMENTS**: Give concrete suggestions for what to add, change, or practice. Be specific about what would make this answer stronger for {company_name} and this role.

Write feedback as if you're a caring, professional coach talking to the candidate directly. Use natural language. DO NOT list numbers, scores, or statistics. Instead, describe what was good and what needs work in human terms.

Return ONLY a valid JSON object with this exact structure:
{{
    "feedback": [
        "First bullet point feedback",
        "Second bullet point feedback",
        "Third bullet point feedback",
        "Fourth bullet point feedback"
    ]
}}

Do not include any additional text, explanations, or markdown formatting outside the JSON object."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, List[str]]:
        """
        Parse the API response and extract feedback JSON.
        
        Args:
            response_text: Raw response text from Gemini API
        
        Returns:
            Dictionary with feedback bullet points
        """
        # Try to extract JSON from the response
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        
        response_text = response_text.strip()
        
        try:
            # Parse JSON
            feedback_dict = json.loads(response_text)
            
            # Ensure it has the correct structure
            if "feedback" in feedback_dict and isinstance(feedback_dict["feedback"], list):
                return feedback_dict
            else:
                # If structure is wrong, wrap it
                return {"feedback": [str(item) for item in feedback_dict.get("feedback", [])]}
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract bullet points manually
            lines = response_text.split('\n')
            feedback_points = []
            
            for line in lines:
                line = line.strip()
                # Look for bullet points (various formats)
                if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                    feedback_points.append(line.lstrip('-*•').strip())
                elif line.startswith(('1.', '2.', '3.', '4.')):
                    feedback_points.append(line.split('.', 1)[1].strip() if '.' in line else line)
            
            # If we extracted points, return them (limit to 4)
            if feedback_points:
                return {"feedback": feedback_points[:4]}
            
            # Fallback: return error message
            return {
                "feedback": [
                    "Error parsing feedback. Original response:",
                    response_text[:200]  # First 200 chars
                ]
            }
    
    def save_feedback(self, feedback: Dict[str, List[str]], output_path: str):
        """
        Save feedback to a JSON file.
        
        Args:
            feedback: Feedback dictionary with bullet points
            output_path: Path where to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)


def generate_interview_feedback(
    company_name: str,
    job_description: str,
    question_text: str,
    speech_confidence_json_path: str,
    body_language_json_path: str,
    eye_contact_json_path: str,
    modulation_json_path: str,
    output_json_path: Optional[str] = None,
    api_key: str = None
) -> Dict[str, List[str]]:
    """
    Convenience function to generate interview feedback.
    
    Args:
        company_name: Name of the company
        job_description: Description of the job position
        question_text: The interview question that was answered
        speech_confidence_json_path: Path to speech confidence analysis JSON
        body_language_json_path: Path to body language analysis JSON
        eye_contact_json_path: Path to eye contact analysis JSON
        modulation_json_path: Path to speech modulation analysis JSON
        output_json_path: Optional path to save the feedback JSON file
        api_key: Google Gemini API key (optional, uses env var if not provided)
    
    Returns:
        A dictionary with feedback containing 4 bullet points
    """
    generator = InterviewFeedbackGenerator(api_key)
    feedback = generator.generate_feedback(
        company_name=company_name,
        job_description=job_description,
        question_text=question_text,
        speech_confidence_json_path=speech_confidence_json_path,
        body_language_json_path=body_language_json_path,
        eye_contact_json_path=eye_contact_json_path,
        modulation_json_path=modulation_json_path
    )
    
    if output_json_path:
        generator.save_feedback(feedback, output_json_path)
    
    return feedback
