"""
Module to generate HR and situational interview questions using Google Gemini API.
"""

import os
import json
from typing import Dict, List
import google.generativeai as genai


class InterviewQuestionGenerator:
    """
    A class to generate interview questions for a given company and job description.
    
    Generates 2 questions total:
    - 1 Introduction question (asks candidate to introduce themselves)
    - 1 Regular HR question (about skills, experience, or motivation)
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
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    def generate_questions(self, company_name: str, job_description: str) -> Dict[str, List[str]]:
        """
        Generate interview questions for a specific company and job.
        
        Args:
            company_name: Name of the company
            job_description: Description of the job position
        
        Returns:
            A dictionary with question types as keys and lists of questions as values.
        """
        prompt = self._create_prompt(company_name, job_description)
        
        response = self.model.generate_content(prompt)
        questions = self._parse_response(response.text)
        
        return questions
    
    def _create_prompt(self, company_name: str, job_description: str) -> str:
        """
        Create the prompt for Gemini API.
        
        Args:
            company_name: Name of the company
            job_description: Description of the job position
        
        Returns:
            A formatted prompt string
        """
        prompt = f"""Generate exactly 2 interview questions for a job interview at {company_name} for the following position:

Job Description:
{job_description}

First, infer the seniority level of the role (e.g., intern, entry-level, junior, intermediate, senior) based on the job description.
Then, tailor the complexity, depth, and expectations of the questions to match that level:

For intern or entry-level roles: keep questions concise, approachable, and focused on foundational skills, learning ability, coursework, projects, teamwork, and motivation. Avoid advanced technical depth, leadership-heavy scenarios, or highly abstract questions.

For intermediate roles: include moderate depth, practical experience, and problem-solving responsibility.

For senior roles: allow for deeper reflection, ownership, leadership, and strategic thinking.

Make sure all questions are specific to {company_name} and the responsibilities described, realistic for an actual interview, and clearly worded (not overly long or complex).

Provide the questions in exactly the following format and structure:

QUESTION 1 (INTRODUCTION):
[One introduction question that asks the candidate to introduce themselves, tailored to the role level]

QUESTION 2 (REGULAR):
[One regular HR question about skills, experience, or motivation, appropriate to the role level]

Do not add explanations, headers, or extra text outside the two questions."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, List[str]]:
        """
        Parse the API response and extract questions.
        
        Args:
            response_text: Raw response text from Gemini API
        
        Returns:
            Dictionary with question categories and their questions
        """
        questions = {
            "introduction": [],
            "regular": [],
            "situational": []
        }
        
        lines = response_text.strip().split("\n")
        current_question = ""
        current_category = None
        
        for line in lines:
            line = line.strip()
            
            if "INTRODUCTION" in line.upper():
                if current_question and current_category:
                    questions[current_category].append(current_question.strip())
                current_category = "introduction"
                current_question = ""
            elif "REGULAR" in line.upper():
                if current_question and current_category:
                    questions[current_category].append(current_question.strip())
                current_category = "regular"
                current_question = ""
            elif "SITUATIONAL" in line.upper():
                if current_question and current_category:
                    questions[current_category].append(current_question.strip())
                current_category = "situational"
                current_question = ""
            elif line and not line.startswith("QUESTION") and line != "[" and current_category:
                # Clean up the line
                line = line.lstrip("[").rstrip("]")
                if line:
                    if current_question:
                        current_question += " " + line
                    else:
                        current_question = line
        
        # Add the last question
        if current_question and current_category:
            questions[current_category].append(current_question.strip())
        
        return questions
    
    def format_questions_for_display(self, questions: Dict[str, List[str]]) -> str:
        """
        Format the generated questions for display.
        
        Args:
            questions: Dictionary of questions organized by category
        
        Returns:
            A formatted string with all questions
        """
        output = "Generated Interview Questions:\n"
        output += "=" * 50 + "\n\n"
        
        question_num = 1
        
        # Introduction question first
        if questions["introduction"]:
            output += f"Question {question_num} (Introduction):\n"
            output += questions["introduction"][0] + "\n\n"
            question_num += 1
        
        # Regular questions
        for regular_q in questions["regular"]:
            output += f"Question {question_num} (Regular):\n"
            output += regular_q + "\n\n"
            question_num += 1
        
        # Situational questions last
        for situational_q in questions["situational"]:
            output += f"Question {question_num} (Situational):\n"
            output += situational_q + "\n\n"
            question_num += 1
        
        return output


def generate_interview_questions(company_name: str, job_description: str, api_key: str = None) -> Dict[str, List[str]]:
    """
    Convenience function to generate interview questions.
    
    Args:
        company_name: Name of the company
        job_description: Description of the job position
        api_key: Google Gemini API key (optional, uses env var if not provided)
    
    Returns:
        A dictionary with question types and their questions
    """
    generator = InterviewQuestionGenerator(api_key)
    return generator.generate_questions(company_name, job_description)
