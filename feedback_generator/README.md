# Interview Feedback Generator

A Python module that generates personalized interview feedback using Google's Gemini API. Takes company name, job description, question text, and all 4 analysis JSON files (speech confidence, body language, eye contact, and speech modulation) to generate 4 bullet point feedback in JSON format.

## Features

- Generates 4 actionable bullet points of feedback per interview question
- Integrates results from 4 analysis modules:
  - Speech Confidence Analysis
  - Body Language Analysis
  - Eye Contact Analysis
  - Speech Modulation Analysis
- Tailored feedback based on company and job description
- Clean JSON output format
- Easy integration into other projects

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your Gemini API key:**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set the environment variable:
     ```bash
     # On Windows (PowerShell)
     $env:GEMINI_API_KEY="your-api-key-here"
     
     # On Windows (Command Prompt)
     set GEMINI_API_KEY=your-api-key-here
     
     # On macOS/Linux
     export GEMINI_API_KEY="your-api-key-here"
     ```

## Usage

### Basic Usage

```python
from feedback_generator import InterviewFeedbackGenerator

# Initialize the generator
generator = InterviewFeedbackGenerator()

# Generate feedback
company_name = "Google"
job_description = "Senior Software Engineer - Backend"
question_text = "Tell me about yourself and why you're interested in this role."

feedback = generator.generate_feedback(
    company_name=company_name,
    job_description=job_description,
    question_text=question_text,
    speech_confidence_json_path="path/to/speech_confidence_analysis.json",
    body_language_json_path="path/to/body_language_analysis.json",
    eye_contact_json_path="path/to/eye_contact_analysis.json",
    modulation_json_path="path/to/modulation_analysis.json"
)

# Print feedback
for i, point in enumerate(feedback["feedback"], 1):
    print(f"{i}. {point}")
```

### Using the Convenience Function

```python
from feedback_generator import generate_interview_feedback

# Generate feedback and save to file
feedback = generate_interview_feedback(
    company_name="Apple",
    job_description="iOS Developer with 3+ years experience",
    question_text="Describe a challenging project you worked on.",
    speech_confidence_json_path="WIN_20260117_06_08_56_Pro_speech_confidence_analysis.json",
    body_language_json_path="WIN_20260117_06_08_56_Pro_body_language_analysis.json",
    eye_contact_json_path="WIN_20260117_06_08_56_Pro_eye_contact_analysis.json",
    modulation_json_path="WIN_20260117_06_08_56_Pro_modulation_analysis.json",
    output_json_path="feedback_output.json"
)
```

### Example: Using with Multiple Questions

```python
from feedback_generator import InterviewFeedbackGenerator

generator = InterviewFeedbackGenerator()

questions = [
    "Tell me about yourself.",
    "Why do you want to work here?",
    "Describe a time when you had to handle a difficult situation."
]

base_path = "WIN_20260117_06_08_56_Pro"
company_name = "Tech Corp"
job_description = "Software Engineer"

for i, question in enumerate(questions, 1):
    feedback = generator.generate_feedback(
        company_name=company_name,
        job_description=job_description,
        question_text=question,
        speech_confidence_json_path=f"{base_path}_speech_confidence_analysis.json",
        body_language_json_path=f"{base_path}_body_language_analysis.json",
        eye_contact_json_path=f"{base_path}_eye_contact_analysis.json",
        modulation_json_path=f"{base_path}_modulation_analysis.json"
    )
    
    # Save feedback
    generator.save_feedback(feedback, f"question_{i}_feedback.json")
```

## Output Format

The module returns a dictionary with the following structure:

```json
{
  "feedback": [
    "First bullet point of constructive feedback",
    "Second bullet point of constructive feedback",
    "Third bullet point of constructive feedback",
    "Fourth bullet point of constructive feedback"
  ]
}
```

Each feedback point is:
- Specific and actionable
- References analysis data where relevant
- Balances positive reinforcement with areas for improvement
- Tailored to the company and job role

## Required JSON File Formats

The module expects JSON files from the following analysis modules:

1. **Speech Confidence Analysis** (`*_speech_confidence_analysis.json`):
   - Contains `confidence_score`, `assessment`, `interpretation`, `recommendations`

2. **Body Language Analysis** (`*_body_language_analysis.json`):
   - Contains `overall_score`, `assessment`, `interpretation`, `recommendations`, `details`

3. **Eye Contact Analysis** (`*_eye_contact_analysis.json`):
   - Contains `overall_score`, `assessment`, `interpretation`, `recommendations`, `details`

4. **Speech Modulation Analysis** (`*_modulation_analysis.json`):
   - Contains `summary` (speech_rate_wpm, filler_words, pauses, sentiment), `sentiment_details`, `fillers`, `pauses`, `transcript`

## Module Structure

- `feedback_generator.py` - Main module containing `InterviewFeedbackGenerator` class
- `requirements.txt` - Python dependencies
- `README.md` - This file

## API Reference

### InterviewFeedbackGenerator

#### `__init__(api_key: str = None)`
Initialize the generator with an optional API key. If not provided, reads from `GEMINI_API_KEY` environment variable.

#### `generate_feedback(company_name: str, job_description: str, question_text: str, speech_confidence_json_path: str, body_language_json_path: str, eye_contact_json_path: str, modulation_json_path: str) -> Dict[str, List[str]]`
Generate feedback based on all analysis results.

#### `save_feedback(feedback: Dict[str, List[str]], output_path: str)`
Save feedback to a JSON file.

### Functions

#### `generate_interview_feedback(company_name: str, job_description: str, question_text: str, speech_confidence_json_path: str, body_language_json_path: str, eye_contact_json_path: str, modulation_json_path: str, output_json_path: Optional[str] = None, api_key: str = None) -> Dict[str, List[str]]`
Convenience function to generate interview feedback in one call. Optionally saves to a JSON file.

## Requirements

- Python 3.7+
- google-generativeai package
- Valid Google Gemini API key
- JSON files from all 4 analysis modules (speech confidence, body language, eye contact, modulation)
