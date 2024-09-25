# Use a base Python image
FROM python:3.9-slim

# Set a working directory for the app
WORKDIR /app

# Install system dependencies (for Whisper, Torch, and ffmpeg)
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file (if you are using one) or manually install dependencies
# Alternatively, you can create requirements.txt and add it here
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Install Python dependencies directly
RUN pip install flask \
    git+https://github.com/openai/whisper.git \
    syllapy \
    torch

# Copy all application files to the working directory
COPY . /app

# Expose port 5000 to the outside world
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Start the Flask app
CMD ["flask", "run"]
