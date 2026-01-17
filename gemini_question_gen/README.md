# Interview Question Generator

A Python module that generates interview questions for job candidates using Google's Gemini API.

## Features

- Generates 5 interview questions total:
  - 1 Introduction question (asks candidate to introduce themselves)
  - 2 Regular HR questions (about skills, experience, motivation)
  - 2 Situational questions (describes scenarios the candidate might face)
- Customizable by company name and job description
- Clean, organized output
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
from question_generator import InterviewQuestionGenerator

# Initialize the generator
generator = InterviewQuestionGenerator()

# Generate questions
company_name = "Google"
job_description = "Senior Software Engineer - Backend"

questions = generator.generate_questions(company_name, job_description)

# Display formatted output
print(generator.format_questions_for_display(questions))
```

### Using the Convenience Function

```python
from question_generator import generate_interview_questions

# Quick generation
questions = generate_interview_questions(
    company_name="Apple",
    job_description="iOS Developer with 3+ years experience"
)
```

### Access Questions by Category

```python
questions = generator.generate_questions(company_name, job_description)

# Access specific question types
introduction = questions["introduction"]  # List with 1 question
regular = questions["regular"]            # List with 2 questions
situational = questions["situational"]    # List with 2 questions
```

## Running the Example

```bash
python example.py
```

## Output Format

The module returns a dictionary with three categories:

```python
{
    "introduction": ["Tell me about yourself and your background..."],
    "regular": ["What attracted you to this role?", "How do you handle deadlines?"],
    "situational": ["Tell me about a time when...", "Describe a situation where..."]
}
```

## Module Structure

- `question_generator.py` - Main module containing `InterviewQuestionGenerator` class
- `example.py` - Example usage script
- `requirements.txt` - Python dependencies
- `README.md` - This file

## API Reference

### InterviewQuestionGenerator

#### `__init__(api_key: str = None)`
Initialize the generator with an optional API key. If not provided, reads from `GEMINI_API_KEY` environment variable.

#### `generate_questions(company_name: str, job_description: str) -> Dict[str, List[str]]`
Generate interview questions for a specific company and job.

#### `format_questions_for_display(questions: Dict[str, List[str]]) -> str`
Format the generated questions for display.

### Functions

#### `generate_interview_questions(company_name: str, job_description: str, api_key: str = None) -> Dict[str, List[str]]`
Convenience function to generate interview questions in one call.

## Requirements

- Python 3.7+
- google-generativeai package
- Valid Google Gemini API key
