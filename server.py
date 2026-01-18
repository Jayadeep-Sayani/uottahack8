"""
Flask API server for the interview preparation system.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "gemini_question_gen"))
sys.path.insert(0, str(Path(__file__).parent / "eleven_labs_tts"))
sys.path.insert(0, str(Path(__file__).parent / "body_language_module"))
sys.path.insert(0, str(Path(__file__).parent / "confidence_analysis_module"))
sys.path.insert(0, str(Path(__file__).parent / "speech_modulation"))
sys.path.insert(0, str(Path(__file__).parent / "feedback_generator"))

from question_generator import InterviewQuestionGenerator
from text_to_speech import TextToSpeech
from body_language_module.body_language_analyzer import analyze_body_language
from confidence_analysis_module import analyze_speech
from speech_modulation_analysis import SpeechModulationAnalyzer
from feedback_generator import InterviewFeedbackGenerator
import json

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


@app.route('/api/clear-recordings', methods=['POST'])
def clear_recordings():
    """
    Clear all recordings from the user_recordings directory and feedback folder.
    Called at the start of each new interview.
    """
    try:
        recordings_dir = Path(__file__).parent / "user_recordings"
        feedback_dir = Path(__file__).parent / "interview_feedback"
        
        # Create directories if they don't exist
        recordings_dir.mkdir(exist_ok=True)
        feedback_dir.mkdir(exist_ok=True)
        
        # Delete all files in the recordings directory
        recordings_deleted = 0
        for file_path in recordings_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
                recordings_deleted += 1
        
        # Delete all files in the feedback directory
        feedback_deleted = 0
        for file_path in feedback_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
                feedback_deleted += 1
        
        print(f"✓ Cleared {recordings_deleted} file(s) from user_recordings directory")
        print(f"✓ Cleared {feedback_deleted} file(s) from interview_feedback directory")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {recordings_deleted} recording(s) and {feedback_deleted} feedback file(s)',
            'recordingsDeleted': recordings_deleted,
            'feedbackDeleted': feedback_deleted
        }), 200
        
    except Exception as e:
        print(f"Error clearing recordings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error clearing recordings: {str(e)}'
        }), 500


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
    Saves recordings to the user_recordings folder and converts webm to mp4.
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
        
        # Save as webm first (browser format)
        webm_filename = f"user_answer_{question_num}.webm"
        webm_path = recordings_dir / webm_filename
        audio_file.save(webm_path)
        
        # Convert webm to mp4 using ffmpeg
        mp4_filename = f"user_answer_{question_num}.mp4"
        mp4_path = recordings_dir / mp4_filename
        
        try:
            # Use ffmpeg to convert webm to mp4
            subprocess.run([
                'ffmpeg',
                '-i', str(webm_path),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                '-y',  # Overwrite output file
                str(mp4_path)
            ], check=True, capture_output=True, text=True)
            
            # Delete the webm file after successful conversion
            webm_path.unlink()
            
            print(f"✓ Recording converted and saved: {mp4_filename}")
            print(f"  Path: {mp4_path}")
            print(f"  Size: {mp4_path.stat().st_size} bytes")
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': mp4_filename,
                    'path': str(mp4_path),
                    'questionNumber': question_num,
                    'size': mp4_path.stat().st_size
                },
                'message': 'Recording saved and converted to MP4 successfully'
            }), 200
            
        except subprocess.CalledProcessError as e:
            # If ffmpeg conversion fails, keep the webm file
            print(f"Warning: FFmpeg conversion failed: {e.stderr}")
            print(f"Keeping webm file: {webm_filename}")
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': webm_filename,
                    'path': str(webm_path),
                    'questionNumber': question_num,
                    'size': webm_path.stat().st_size
                },
                'message': 'Recording saved as webm (mp4 conversion failed)',
                'warning': 'FFmpeg not available or conversion failed'
            }), 200
            
        except FileNotFoundError:
            # FFmpeg not found, keep webm file
            print(f"Warning: FFmpeg not found. Keeping webm file: {webm_filename}")
            
            return jsonify({
                'success': True,
                'data': {
                    'filename': webm_filename,
                    'path': str(webm_path),
                    'questionNumber': question_num,
                    'size': webm_path.stat().st_size
                },
                'message': 'Recording saved as webm (FFmpeg not available)',
                'warning': 'FFmpeg not found in system PATH'
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


def extract_audio_from_mp4(video_path: Path) -> Path:
    """
    Extract audio from MP4 file and save as WAV using ffmpeg.
    
    Args:
        video_path: Path to MP4 video file
    
    Returns:
        Path to extracted WAV audio file
    """
    audio_path = video_path.with_suffix(".wav")
    
    # Use ffmpeg command line to extract audio
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit audio codec
        "-ar", "44100",  # Sample rate
        "-ac", "2",  # Stereo channels
        "-y",  # Overwrite output file if it exists
        str(audio_path)
    ]
    
    try:
        # Run ffmpeg, suppress output
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return audio_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg extraction failed: {e.stderr}")
    except FileNotFoundError:
        raise Exception("FFmpeg not found in system PATH")


@app.route('/api/analyze-recordings', methods=['POST'])
def analyze_recordings():
    """
    Analyze all MP4 recordings in user_recordings directory.
    Generates JSON files for body language, speech confidence, and speech modulation analysis.
    Then generates feedback for each recording.
    
    Expects JSON body with:
    - companyName (optional): Company name for feedback generation
    - jobDescription (optional): Job description for feedback generation
    - questions (optional): List of question objects with 'text' field
    """
    try:
        data = request.get_json() or {}
        company_name = data.get('companyName', '')
        job_description = data.get('jobDescription', '')
        questions_list = data.get('questions', [])
        
        recordings_dir = Path(__file__).parent / "user_recordings"
        feedback_dir = Path(__file__).parent / "interview_feedback"
        feedback_dir.mkdir(exist_ok=True)
        
        if not recordings_dir.exists():
            return jsonify({
                'success': False,
                'error': 'user_recordings directory does not exist'
            }), 404
        
        # Get all MP4 files
        mp4_files = sorted(list(recordings_dir.glob("*.mp4")))
        
        if not mp4_files:
            return jsonify({
                'success': False,
                'error': 'No MP4 files found in user_recordings directory'
            }), 404
        
        print(f"=" * 60)
        print(f"Analyzing {len(mp4_files)} recording(s)")
        print(f"=" * 60)
        
        results = {}
        
        for video_path in mp4_files:
            base_name = video_path.stem
            print(f"\nAnalyzing: {video_path.name}")
            
            video_results = {
                'video_file': video_path.name,
                'body_language': None,
                'speech_confidence': None,
                'speech_modulation': None,
                'errors': []
            }
            
            # 1. Body Language Analysis
            try:
                print(f"  → Analyzing body language...")
                body_language_results = analyze_body_language(str(video_path))
                body_language_json = recordings_dir / f"{base_name}_body_language_analysis.json"
                with open(body_language_json, 'w') as f:
                    json.dump(body_language_results, f, indent=2)
                video_results['body_language'] = str(body_language_json)
                print(f"  ✓ Body language analysis saved: {body_language_json.name}")
            except Exception as e:
                error_msg = f"Body language analysis failed: {str(e)}"
                print(f"  ✗ {error_msg}")
                video_results['errors'].append(error_msg)
            
            # 2. Speech Confidence Analysis
            try:
                print(f"  → Analyzing speech confidence...")
                
                # Extract audio from MP4
                try:
                    audio_path = extract_audio_from_mp4(video_path)
                    print(f"  ✓ Audio extracted: {audio_path.name}")
                except Exception as e:
                    raise Exception(f"Audio extraction failed: {str(e)}")
                
                # Analyze speech
                try:
                    speech_results = analyze_speech(str(audio_path))
                    speech_json = recordings_dir / f"{base_name}_speech_confidence_analysis.json"
                    with open(speech_json, 'w') as f:
                        json.dump(speech_results, f, indent=2)
                    video_results['speech_confidence'] = str(speech_json)
                    print(f"  ✓ Speech confidence analysis saved: {speech_json.name}")
                    
                    # Clean up extracted audio file
                    try:
                        audio_path.unlink()
                    except:
                        pass  # Ignore cleanup errors
                except Exception as e:
                    raise Exception(f"Speech analysis failed: {str(e)}")
                
            except Exception as e:
                error_msg = f"Speech confidence analysis failed: {str(e)}"
                print(f"  ✗ {error_msg}")
                video_results['errors'].append(error_msg)
                # Clean up audio file if it exists
                audio_path = video_path.with_suffix(".wav")
                if audio_path.exists():
                    try:
                        audio_path.unlink()
                    except:
                        pass
            
            # 3. Speech Modulation Analysis
            try:
                print(f"  → Analyzing speech modulation...")
                try:
                    modulation_analyzer = SpeechModulationAnalyzer()
                    # Temporarily set output_dir to save in same location as other analyses
                    original_output_dir = modulation_analyzer.output_dir
                    modulation_analyzer.output_dir = recordings_dir
                    
                    # Run analysis - this will save the file to self.output_dir
                    modulation_results = modulation_analyzer.analyze(str(video_path))
                    
                    # The analyze method saves the file using output_dir, so get the expected path
                    modulation_json = recordings_dir / f"{base_name}_modulation_analysis.json"
                    
                    # Verify file was created (in case analyze() saved to a different location)
                    if not modulation_json.exists():
                        # Check if it was saved to the original output_dir instead
                        possible_path = original_output_dir / f"{base_name}_modulation_analysis.json"
                        if possible_path.exists():
                            # Move it to the correct location
                            import shutil
                            shutil.move(str(possible_path), str(modulation_json))
                            print(f"  ✓ Moved modulation file to correct location")
                        else:
                            raise Exception(f"Modulation analysis file was not created at expected path")
                    
                    # Restore original output_dir
                    modulation_analyzer.output_dir = original_output_dir
                    video_results['speech_modulation'] = str(modulation_json)
                    print(f"  ✓ Speech modulation analysis saved: {modulation_json.name}")
                    
                except ValueError as e:
                    # AssemblyAI API key not found - skip this analysis
                    error_msg = f"Speech modulation analysis skipped: {str(e)}"
                    print(f"  ⚠ {error_msg}")
                    video_results['errors'].append(error_msg)
                except Exception as e:
                    raise Exception(f"Speech modulation analysis failed: {str(e)}")
            except Exception as e:
                error_msg = f"Speech modulation analysis failed: {str(e)}"
                print(f"  ✗ {error_msg}")
                video_results['errors'].append(error_msg)
            
            results[base_name] = video_results
        
        # Generate feedback for each recording if we have all required data
        if company_name and job_description and questions_list:
            print(f"\n" + "=" * 60)
            print(f"Generating Feedback")
            print(f"=" * 60)
            
            # Create a placeholder eye_contact JSON file (since we're not doing eye contact analysis yet)
            placeholder_eye_contact = {
                "overall_score": 0.5,
                "assessment": "NOT_ANALYZED",
                "interpretation": "Eye contact analysis not performed in this session",
                "recommendations": ["Eye contact analysis will be added in future updates"]
            }
            placeholder_eye_contact_path = recordings_dir / "placeholder_eye_contact.json"
            with open(placeholder_eye_contact_path, 'w') as f:
                json.dump(placeholder_eye_contact, f, indent=2)
            
            try:
                feedback_generator = InterviewFeedbackGenerator()
            except ValueError as e:
                print(f"⚠ Feedback generation skipped: {str(e)}")
                feedback_generator = None
            
            if feedback_generator:
                for video_path in mp4_files:
                    base_name = video_path.stem
                    # Extract question number from base_name (e.g., "user_answer_1" -> 1)
                    try:
                        question_num = int(base_name.split('_')[-1])
                        if 1 <= question_num <= len(questions_list):
                            question_text = questions_list[question_num - 1].get('text', '')
                        else:
                            question_text = questions_list[0].get('text', '') if questions_list else ''
                    except (ValueError, IndexError):
                        question_text = questions_list[0].get('text', '') if questions_list else ''
                    
                    if not question_text:
                        print(f"  ⚠ Skipping feedback for {base_name}: No question text available")
                        continue
                    
                    # Get analysis file paths
                    body_language_json = recordings_dir / f"{base_name}_body_language_analysis.json"
                    speech_json = recordings_dir / f"{base_name}_speech_confidence_analysis.json"
                    modulation_json = recordings_dir / f"{base_name}_modulation_analysis.json"
                    
                    # Check if all required analysis files exist
                    if not body_language_json.exists() or not speech_json.exists() or not modulation_json.exists():
                        print(f"  ⚠ Skipping feedback for {base_name}: Missing analysis files")
                        continue
                    
                    try:
                        print(f"\n  → Generating feedback for {base_name}...")
                        feedback = feedback_generator.generate_feedback(
                            company_name=company_name,
                            job_description=job_description,
                            question_text=question_text,
                            speech_confidence_json_path=str(speech_json),
                            body_language_json_path=str(body_language_json),
                            eye_contact_json_path=str(placeholder_eye_contact_path),
                            modulation_json_path=str(modulation_json)
                        )
                        
                        # Save feedback
                        feedback_json = feedback_dir / f"{base_name}_feedback.json"
                        feedback_generator.save_feedback(feedback, str(feedback_json))
                        
                        results[base_name]['feedback'] = str(feedback_json)
                        print(f"  ✓ Feedback saved: {feedback_json.name}")
                        
                    except Exception as e:
                        error_msg = f"Feedback generation failed for {base_name}: {str(e)}"
                        print(f"  ✗ {error_msg}")
                        if 'errors' not in results[base_name]:
                            results[base_name]['errors'] = []
                        results[base_name]['errors'].append(error_msg)
            
            # Clean up placeholder file
            if placeholder_eye_contact_path.exists():
                try:
                    placeholder_eye_contact_path.unlink()
                except:
                    pass
            
            # Generate overall feedback from all individual feedback files
            if feedback_generator:
                try:
                    print(f"\n" + "=" * 60)
                    print(f"Generating Overall Feedback")
                    print(f"=" * 60)
                    
                    # Load all individual feedback files
                    all_feedback_files = sorted(list(feedback_dir.glob("user_answer_*_feedback.json")))
                    
                    if all_feedback_files:
                        print(f"  → Loading {len(all_feedback_files)} feedback file(s)...")
                        all_feedback_data = []
                        
                        for feedback_file in all_feedback_files:
                            try:
                                with open(feedback_file, 'r') as f:
                                    feedback_data = json.load(f)
                                    all_feedback_data.append(feedback_data)
                            except Exception as e:
                                print(f"  ⚠ Failed to load {feedback_file.name}: {e}")
                        
                        if all_feedback_data:
                            print(f"  → Generating overall feedback from {len(all_feedback_data)} question(s)...")
                            
                            # Create the prompt
                            feedback_text = ""
                            for i, feedback in enumerate(all_feedback_data, 1):
                                feedback_text += f"\n\n--- Question {i} Feedback ---\n"
                                if isinstance(feedback, dict) and 'feedback' in feedback:
                                    for bullet in feedback['feedback']:
                                        feedback_text += f"- {bullet}\n"
                                else:
                                    feedback_text += str(feedback) + "\n"
                            
                            prompt = """
        You are an expert interview coach. Below is the analysis from some individual interview questions. 
        Provide a comprehensive overall feedback report in JSON format.
        
        The JSON should have the following structure:
        {
          "summary": "A brief overall summary of the candidate's performance",
          "strengths": ["Strength 1", "Strength 2", ...],
          "areas_for_improvement": ["Area 1", "Area 2", ...],
          "consistency_analysis": "An evaluation of how consistent the candidate was across questions",
          "communication_style": "Analysis of the candidate's communication style",
          "confidence_score": "A score from 1-10",
          "final_recommendation": "A clear recommendation written as if speaking directly to the candidate using 'you' (e.g., 'Based on your performance, I recommend...' or 'You demonstrated strong skills in...')"
        }
        
        IMPORTANT: The "final_recommendation" field should be written as if the interviewer is speaking directly to the candidate, using "you" to refer to them. For example: "Based on your performance across all questions, you demonstrated strong technical knowledge and clear communication. However, you could benefit from... We recommend..."
        
        Ensure the response is ONLY the JSON object, with no markdown formatting or extra text.
        
        Individual Question Feedback:
        """ + feedback_text
                            
                            # Generate overall feedback using Gemini
                            response = feedback_generator.model.generate_content(prompt)
                            response_text = response.text.strip()
                            
                            # Remove markdown code blocks if present
                            if response_text.startswith("```json"):
                                response_text = response_text[7:]
                            elif response_text.startswith("```"):
                                response_text = response_text[3:]
                            
                            if response_text.endswith("```"):
                                response_text = response_text[:-3]
                            
                            response_text = response_text.strip()
                            
                            try:
                                overall_feedback = json.loads(response_text)
                                
                                # Save overall feedback
                                overall_feedback_json = feedback_dir / "overall_feedback.json"
                                with open(overall_feedback_json, 'w') as f:
                                    json.dump(overall_feedback, f, indent=2, ensure_ascii=False)
                                
                                print(f"  ✓ Overall feedback saved: {overall_feedback_json.name}")
                                
                            except json.JSONDecodeError as e:
                                print(f"  ✗ Failed to parse overall feedback JSON: {e}")
                                print(f"  Response: {response_text[:200]}...")
                        else:
                            print(f"  ⚠ No valid feedback data found to generate overall feedback")
                    else:
                        print(f"  ⚠ No individual feedback files found")
                        
                except Exception as e:
                    print(f"  ✗ Overall feedback generation failed: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        print(f"\n" + "=" * 60)
        print(f"Analysis Complete!")
        print(f"=" * 60)
        
        return jsonify({
            'success': True,
            'message': f'Analyzed {len(mp4_files)} recording(s)',
            'results': results
        }), 200
        
    except Exception as e:
        print(f"Error analyzing recordings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error analyzing recordings: {str(e)}'
        }), 500


@app.route('/api/get-overall-feedback', methods=['GET'])
def get_overall_feedback():
    """
    Get the overall feedback JSON file.
    """
    try:
        feedback_dir = Path(__file__).parent / "interview_feedback"
        overall_feedback_path = feedback_dir / "overall_feedback.json"
        
        if not overall_feedback_path.exists():
            return jsonify({
                'success': False,
                'error': 'Overall feedback not found'
            }), 404
        
        with open(overall_feedback_path, 'r') as f:
            overall_feedback = json.load(f)
        
        return jsonify(overall_feedback), 200
        
    except Exception as e:
        print(f"Error getting overall feedback: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error getting overall feedback: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
