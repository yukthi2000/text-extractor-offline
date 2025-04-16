from flask import Flask, request, jsonify ,send_file
import whisper
import os
from flask_cors import CORS
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment
import tempfile
import subprocess

app = Flask(__name__)
CORS(app)

model = whisper.load_model("base")


def extract_audio(video_path, audio_path):
    cmd = [
        "ffmpeg", "-i", video_path,
        "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le", "-y",
        audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def reduce_noise(input_file, output_file):
    # Convert MP3 to WAV using pydub
    audio = AudioSegment.from_file(input_file)
    audio.export("temp.wav", format="wav")

    # Read the WAV file
    data, rate = sf.read("temp.wav")

    # Perform noise reduction
    reduced_noise = nr.reduce_noise(y=data, sr=rate)

    # Save the cleaned audio
    sf.write(output_file, reduced_noise, rate)

    # Clean up temporary file
    os.remove("temp.wav")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded!"}), 400

    file = request.files["file"]
    file_path = "uploaded_audio.mp3"
    file.save(file_path)

    # Reduce noise
    cleaned_audio_path = "cleaned_audio.wav"
    reduce_noise(file_path, cleaned_audio_path)

    # Transcribe the cleaned audio
    result = model.transcribe(cleaned_audio_path)
    os.remove(file_path)
    os.remove(cleaned_audio_path)

    return jsonify({"text": result["text"]})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)