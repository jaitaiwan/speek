from flask import Flask, render_template, request, redirect, url_for, jsonify
import whisper
import os
import time
from syllapy import count as count_syllables
import matplotlib.pyplot as plt
import numpy as np
import random
import string

# Initialize Flask application
app = Flask(__name__)

# Create the folder to store uploaded audio files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
model = whisper.load_model("base")

def random_string(length=9):
    charset = string.ascii_lowercase + string.digits
    return ''.join(random.choice(charset) for _ in range(length))

# Function to calculate WPM
def calculate_wpm(word_count, elapsed_seconds):
    minutes = elapsed_seconds / 60
    wpm = word_count / minutes if minutes > 0 else 0
    return wpm

# Function to generate and save cadence plot
def generate_cadence_plot(word_intervals):
    plt.plot(np.arange(len(word_intervals)), word_intervals, label="Word Cadence (s)")
    plt.xlabel('Word Index')
    plt.ylabel('Time Between Words (s)')
    plt.title('Word Cadence over Time')
    plt.legend()
    plot_path = random_string() + '-cadence_plot.png'
    plt.savefig(os.path.join('static', plot_path))
    plt.close()
    return plot_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wpm')
def wpm():
    return render_template('wpm.html')

@app.route('/syllable')
def sy():
    return render_template('syllable.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return redirect(url_for('index'))
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    audio_file.save(file_path)

    # Transcribe and analyze the audio file
    start_time = time.time()
    result = model.transcribe(file_path, word_timestamps=True)
    elapsed_time = time.time() - start_time

    # Extract word-level timestamps
    words = []
    word_intervals = []
    prev_end_time = None

    for segment in result['segments']:
        for word_info in segment['words']:
            words.append(word_info['word'])
            if prev_end_time is not None:
                word_intervals.append(word_info['start'] - prev_end_time)
            prev_end_time = word_info['end']

    word_count = len(words)
    wpm = calculate_wpm(word_count, elapsed_time)

    plot_path = generate_cadence_plot(word_intervals)

    if os.path.exists(file_path):
        os.remove(file_path)

    # Return JSON data (text transcription, WPM, plot path)
    return jsonify({
        'transcription': result['text'],
        'word_count': syllable_count,
        'wpm': wpm,
        'plot': plot_path
    })

@app.route('/plot/<path:filename>')
def display_plot(filename):
    return redirect(url_for('static', filename=filename))

if __name__ == '__main__':
    app.run(debug=True)
