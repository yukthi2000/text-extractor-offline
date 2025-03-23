from flask import Flask,request, jsonify
import whisper 
import os
from flask_cors import CORS 



app = Flask(__name__)
CORS(app)

model = whisper.load_model("base")

@app.route("/tanscribe",methods =["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error":"NO file uploaded!"}),400
    
    file = request.files["file"]
    file_path = "uploaded_audio.mp3"
    file.save(file_path)

    result = model.transcribe(file_path)
    os.remove(file_path)

    return jsonify({"text":result["text"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 5000)

