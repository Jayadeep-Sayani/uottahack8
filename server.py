"""
Flask API server for the interview preparation system.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "gemini_question_gen"))
sys.path.insert(0, str(Path(__file__).parent / "eleven_labs_tts"))

from question_generator import InterviewQuestionGenerator
from text_to_speech import TextToSpeech

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize question generator
question_generator = InterviewQuestionGenerator()

# Initialize TTS generator
try:
    tts_generator = TextToSpeech()
except Exception as e:
    print(f"Warning: Could not initialize TTS generator: {e}")
    tts_generator = None


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


@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using ElevenLabs TTS.
    Returns the audio file path or uses browser TTS if ElevenLabs is unavailable.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # If TTS generator is available, use it
        if tts_generator:
            try:
                # Generate speech
                audio_path = tts_generator.generate_speech(
                    text=text,
                    output_filename=f"question_tts_{abs(hash(text)) % 10000}.mp3"
                )
                
                # Return the audio file URL that can be accessed by the frontend
                audio_filename = Path(audio_path).name
                return jsonify({
                    'success': True,
                    'audioUrl': f'/api/audio/{audio_filename}',
                    'method': 'elevenlabs'
                }), 200
            except Exception as e:
                print(f"Error generating TTS with ElevenLabs: {e}")
                # Fall through to browser TTS recommendation
        
        # If ElevenLabs is not available, suggest using browser TTS
        return jsonify({
            'success': True,
            'text': text,
            'method': 'browser',
            'message': 'Use browser SpeechSynthesis API'
        }), 200
        
    except Exception as e:
        print(f"Error in text-to-speech endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to generate speech'}), 500


@app.route('/api/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """
    Serve audio files generated by TTS.
    """
    try:
        # Get the output directory from TTS generator
        if tts_generator:
            audio_dir = Path(tts_generator.output_dir)
        else:
            # Fallback to default output directory
            audio_dir = Path("output")
        
        audio_path = audio_dir / filename
        
        if audio_path.exists():
            return send_file(str(audio_path), mimetype='audio/mpeg')
        else:
            return jsonify({'error': 'Audio file not found'}), 404
    except Exception as e:
        print(f"Error serving audio file: {e}")
        return jsonify({'error': 'Failed to serve audio file'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
