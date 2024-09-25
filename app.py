from flask import Flask, render_template, request, redirect, url_for, jsonify
import whisper
import os
import time
from syllapy import count as count_syllables
import matplotlib.pyplot as plt
import numpy as np

# Initialize Flask application
app = Flask(__name__)

# Create the folder to store uploaded audio files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load Whisper model
model = whisper.load_model("base")

# Function to calculate WPM
def calculate_wpm(syllable_count, elapsed_seconds, syllables_per_word=1.5):
    minutes = elapsed_seconds / 60
    estimated_words = syllable_count / syllables_per_word
    wpm = estimated_words / minutes
    return wpm

# Function to count syllables in a sentence
def get_syllable_count(text):
    words = text.split()
    syllable_count = sum(count_syllables(word) for word in words)
    return syllable_count

# Function to generate and save cadence plot
def generate_cadence_plot(syllable_times):
    plt.plot(syllable_times, np.arange(len(syllable_times)), label="Syllable Cadence")
    plt.xlabel('Time (seconds)')
    plt.ylabel('Syllables')
    plt.title('Syllable Cadence over Time')
    plt.legend()
    plot_path = os.path.join(UPLOAD_FOLDER, 'cadence_plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

@app.route('/')
def index():
    return render_template('index.html')

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
    result = model.transcribe(file_path)
    elapsed_time = time.time() - start_time

    # Calculate syllable count
    syllable_count = get_syllable_count(result['text'])
    wpm = calculate_wpm(syllable_count, elapsed_time)

    # Generate mock syllable times for cadence plot (as Whisper doesn't return timestamps per syllable)
    syllable_times = np.linspace(0, elapsed_time, syllable_count)
    plot_path = generate_cadence_plot(syllable_times)

    # Return JSON data (text transcription, WPM, plot path)
    return jsonify({
        'transcription': result['text'],
        'syllable_count': syllable_count,
        'wpm': wpm,
        'plot': plot_path
    })

@app.route('/plot/<path:filename>')
def display_plot(filename):
    return redirect(url_for('static', filename=filename))

if __name__ == '__main__':
    app.run(debug=True)
