# from flask import Flask, request, jsonify ,send_file
# import whisper
# import os
# from flask_cors import CORS
# import noisereduce as nr
# import soundfile as sf
# from pydub import AudioSegment
# import tempfile
# import subprocess
# import io

# app = Flask(__name__)
# CORS(app)

# model = whisper.load_model("small")


# def extract_audio(video_path, audio_path):
#     cmd = [
#         "ffmpeg", "-i", video_path,
#         "-ar", "16000", "-ac", "1",
#         "-c:a", "pcm_s16le", "-y",
#         audio_path
#     ]
#     subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# def extract_and_enhance_audio(video_path, audio_path):
#     """Extract audio from video with enhanced preprocessing"""
#     cmd = [
#         "ffmpeg", "-i", video_path,
#         "-af", "highpass=f=100,lowpass=f=4000,afftdn=nf=-25,dynaudnorm",  # Noise reduction
#         "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",  # Whisper's optimal format
#         "-y", audio_path
#     ]
#     subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# def reduce_noise(input_file, output_file):
#     # Convert MP3 to WAV using pydub
#     audio = AudioSegment.from_file(input_file)
#     audio.export("temp.wav", format="wav")

#     # Read the WAV file
#     data, rate = sf.read("temp.wav")

#     # Perform noise reduction
#     reduced_noise = nr.reduce_noise(y=data, sr=rate)

#     # Save the cleaned audio
#     sf.write(output_file, reduced_noise, rate)

#     # Clean up temporary file
#     os.remove("temp.wav")

# @app.route("/transcribe", methods=["POST"])
# def transcribe():
#     if "file" not in request.files:
#         return jsonify({"error": "No file uploaded!"}), 400

#     file = request.files["file"]
#     file_path = "uploaded_audio.mp3"
#     file.save(file_path)

#     # Reduce noise
#     cleaned_audio_path = "cleaned_audio.wav"
#     reduce_noise(file_path, cleaned_audio_path) 

#     # Transcribe the cleaned audio
#     result = model.transcribe(cleaned_audio_path)
#     os.remove(file_path)
#     os.remove(cleaned_audio_path)

#     return jsonify({"text": result["text"]})

# # @app.route("/vidtranscribe", methods=["POST"])
# # def transcribe_video():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     video_file = request.files['file']
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         video_path = os.path.join(temp_dir, video_file.filename)
#         audio_path = os.path.join(temp_dir, "audio.wav")
#         transcript_path = os.path.join(temp_dir, "transcript.txt")

#         video_file.save(video_path)
#         extract_audio(video_path, audio_path)

#         segments, _ = model.transcribe(audio_path)
#         transcript = ""
#         for segment in segments:
#             transcript += f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}\n"

#         with open(transcript_path, "w", encoding="utf-8") as f:
#             f.write(transcript)

#         return send_file(transcript_path, as_attachment=True, download_name="transcript.txt")


# @app.route("/vidtranscribe", methods=["POST"])
# def transcribe_video():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     video_file = request.files['file']
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         video_path = os.path.join(temp_dir, video_file.filename)
#         audio_path = os.path.join(temp_dir, "audio.wav")
#         transcript_path = os.path.join(temp_dir, "transcript.txt")

#         video_file.save(video_path)
#         # extract_audio(video_path, audio_path)
#         extract_and_enhance_audio(video_path, audio_path)

#         result = model.transcribe(audio_path,
#             language="en",
#             beam_size=5,
#             temperature=(0.0, 0.2, 0.4),  # Multi-temperature sampling
#             initial_prompt="Accurate transcription with timestamps.",
#             word_timestamps=True  # Include word-level timestamps
#         )
#         segments = result.get("segments", [])
        
#         transcript = ""
#         for segment in segments:
#             start = segment.get("start", 0)
#             end = segment.get("end", 0)
#             text = segment.get("text", "")
#             transcript += f" {text}\n"

#         with open(transcript_path, "w", encoding="utf-8") as f:
#             f.write(transcript)

#         # Read the file content and close it before sending
#         with open(transcript_path, "rb") as f:
#             file_content = f.read()
        
#         response = send_file(
#             io.BytesIO(file_content),
#             as_attachment=True,
#             download_name="transcript.txt",
#             mimetype='text/plain'
#         )
        
#         return response

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)



from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import io
from pydub import AudioSegment
from faster_whisper import WhisperModel
import torch

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"


app = Flask(__name__)
CORS(app)

# Check for GPU and set device
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
print(f"Using device: {device}, compute_type: {compute_type}")

# Load Faster-Whisper model (small)
model = WhisperModel("tiny", device=device, compute_type=compute_type)

def chunk_audio(audio_path, chunk_length_ms=10*60*1000, temp_dir=None):
    audio = AudioSegment.from_file(audio_path)
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[start:start+chunk_length_ms]
        chunk_path = os.path.join(temp_dir, f"chunk_{i}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks

def transcribe_chunks(chunk_paths):
    """Transcribes each chunk and returns concatenated transcript."""
    transcript = ""
    for chunk_path in chunk_paths:
        segments, _ = model.transcribe(chunk_path, beam_size=5)
        for segment in segments:
            transcript += f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}\n"
    return transcript

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded!"}), 400

    file = request.files["file"]
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        file.save(temp_audio)
        temp_audio_path = temp_audio.name

    # Chunk the audio
    chunk_paths = chunk_audio(temp_audio_path)
    transcript = transcribe_chunks(chunk_paths)

    os.remove(temp_audio_path)
    return jsonify({"text": transcript})

@app.route("/vidtranscribe", methods=["POST"])
def transcribe_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    video_file = request.files['file']
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, video_file.filename)
        audio_path = os.path.join(temp_dir, "audio.wav")
        transcript_path = os.path.join(temp_dir, "transcript.txt")

        video_file.save(video_path)
        # Extract audio using ffmpeg
        os.system(f'ffmpeg -i "{video_path}" -ar 16000 -ac 1 -c:a pcm_s16le -y "{audio_path}"')

        # Pass temp_dir to chunk_audio
        chunk_paths = chunk_audio(audio_path, temp_dir=temp_dir)
        transcript = transcribe_chunks(chunk_paths)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        with open(transcript_path, "rb") as f:
            file_content = f.read()

        response = send_file(
            io.BytesIO(file_content),
            as_attachment=True,
            download_name="transcript.txt",
            mimetype='text/plain'
        )
        return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
