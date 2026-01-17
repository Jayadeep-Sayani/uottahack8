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

from gemini_question_gen.question_generator import InterviewQuestionGenerator

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

@app.route('/api/save-user-recording', methods=['POST'])
def save_user_recording():
    """
    Endpoint to save user's audio/video recording.
    Saves recordings to the user_recordings folder.
    """
    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        question_num = request.form.get('questionNumber', '1')
        
        # Validate the file
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Create the user_recordings directory if it doesn't exist
        recordings_dir = Path(__file__).parent / "user_recordings"
        recordings_dir.mkdir(exist_ok=True)
        
        # Create filename with question number
        filename = f"user_answer_{question_num}.webm"
        save_path = recordings_dir / filename
        
        # Save the file
        audio_file.save(save_path)
        
        print(f"✓ Recording saved: {filename}")
        print(f"  Path: {save_path}")
        print(f"  Size: {save_path.stat().st_size} bytes")
        
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'path': str(save_path),
                'questionNumber': question_num,
                'size': save_path.stat().st_size
            },
            'message': 'Recording saved successfully'
        }), 200
        
    except Exception as e:
        print(f"Error saving user recording: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error saving recording: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
