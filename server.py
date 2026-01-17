"""
Flask API server for the interview preparation system.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "gemini_question_gen"))

from question_generator import InterviewQuestionGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize question generator
question_generator = InterviewQuestionGenerator()


@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    """
    Generate interview questions based on company name and job description.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        company_name = data.get('companyName', '').strip()
        job_description = data.get('jobDescription', '').strip()
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Generate questions
        questions = question_generator.generate_questions(company_name, job_description)
        
        # Format questions for response
        all_questions = []
        question_num = 1
        
        # Add introduction question
        if questions.get("introduction"):
            all_questions.append({
                "number": question_num,
                "type": "Introduction",
                "text": questions["introduction"][0]
            })
            question_num += 1
        
        # Add regular questions
        for regular_q in questions.get("regular", []):
            all_questions.append({
                "number": question_num,
                "type": "Regular",
                "text": regular_q
            })
            question_num += 1
        
        # Add situational questions
        for situational_q in questions.get("situational", []):
            all_questions.append({
                "number": question_num,
                "type": "Situational",
                "text": situational_q
            })
            question_num += 1
        
        return jsonify({
            'success': True,
            'companyName': company_name,
            'questions': all_questions
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error generating questions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to generate questions. Please try again.'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
