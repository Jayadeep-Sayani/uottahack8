# Multi-stage build for the full-stack interview preparation app

# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY Frontend/package*.json ./
RUN npm install

COPY Frontend/ ./
RUN npm run build

# Stage 2: Python backend with all dependencies
FROM python:3.11-slim

# Install system dependencies including ffmpeg and build tools
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all Python requirements files
COPY requirements.txt ./
COPY body_language_module/requirements.txt ./body_language_module/
COPY confidence_analysis_module/requirements.txt ./confidence_analysis_module/
COPY eleven_labs_tts/requirements.txt ./eleven_labs_tts/
COPY gemini_question_gen/requirements.txt ./gemini_question_gen/
COPY feedback_generator/requirements.txt ./feedback_generator/
COPY speech_modulation/requirements.txt ./speech_modulation/

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r body_language_module/requirements.txt && \
    pip install --no-cache-dir -r confidence_analysis_module/requirements.txt && \
    pip install --no-cache-dir -r eleven_labs_tts/requirements.txt && \
    pip install --no-cache-dir -r gemini_question_gen/requirements.txt && \
    pip install --no-cache-dir -r feedback_generator/requirements.txt && \
    pip install --no-cache-dir -r speech_modulation/requirements.txt

# Install additional dependencies that might be needed
RUN pip install --no-cache-dir \
    SpeechRecognition \
    pydub \
    requests

# Copy backend code
COPY server.py ./
COPY main.py ./
COPY body_language_module/ ./body_language_module/
COPY confidence_analysis_module/ ./confidence_analysis_module/
COPY eleven_labs_tts/ ./eleven_labs_tts/
COPY gemini_question_gen/ ./gemini_question_gen/
COPY feedback_generator/ ./feedback_generator/
COPY speech_modulation/ ./speech_modulation/

# Copy built frontend from builder stage to static directory
COPY --from=frontend-builder /app/frontend/dist ./static

# Create directories for outputs
RUN mkdir -p output user_recordings interview_feedback interview_output

# Expose port (default Flask port, can be overridden with env var)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Default command to run the server
# Note: The server should be configured to serve the frontend static files
CMD ["python", "server.py"]
