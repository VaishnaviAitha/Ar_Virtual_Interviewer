from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import base64
import os
import uuid
import subprocess

from llm.gemini_client import GeminiClient
from stt.whisper_stt import transcribe_audio
from tts.local_tts import synthesize_speech
from conversation.interview_manager import InterviewManager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WEB_AR_DIR = BASE_DIR.parent / "web_ar"

# ------------------------
# App Setup
# ------------------------

app = Flask(__name__, static_folder="web_ar")
CORS(app)

os.makedirs("audio/input", exist_ok=True)
os.makedirs("audio/output", exist_ok=True)

interview_manager = InterviewManager(mode="general")

# ------------------------
# Utils
# ------------------------

def convert_to_wav(input_path, output_path):
    """Convert any audio format to 16kHz mono WAV for Whisper"""
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        output_path
    ], check=True)

def encode_audio_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# ------------------------
# Routes
# ------------------------

@app.route("/")
def index():
    return send_from_directory(WEB_AR_DIR, "index.html")

@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_from_directory(WEB_AR_DIR / "models", filename)
@app.route("/marker/<path:filename>")
def serve_marker(filename):
    return send_from_directory(WEB_AR_DIR / "marker", filename)

@app.route("/start", methods=["GET"])
def start_interview():
    print("\n🎤 Starting new interview session...")

    question = interview_manager.start_interview()
    print(f"ARAI: {question}")

    audio_path = f"audio/output/question_{uuid.uuid4().hex}.mp3"
    synthesize_speech(question, output_path=audio_path)

    audio_base64 = encode_audio_base64(audio_path)

    return jsonify({
        "question": question,
        "audio": audio_base64,
        "ended": False
    })

@app.route("/respond", methods=["POST"])
def handle_response():
    print("\n🎤 Processing user response...")

    data = request.get_json()
    if not data or "audio" not in data:
        return jsonify({"error": "No audio provided"}), 400

    audio_b64 = data["audio"]
    audio_bytes = base64.b64decode(audio_b64)

    raw_path = f"audio/input/user_{uuid.uuid4().hex}.webm"
    wav_path = f"audio/input/user_{uuid.uuid4().hex}.wav"

    with open(raw_path, "wb") as f:
        f.write(audio_bytes)

    convert_to_wav(raw_path, wav_path)

    user_text = transcribe_audio(wav_path)
    print(f"User: {user_text}")

    if user_text.strip().lower() in ["exit", "quit", "stop", "end"]:
        goodbye = "Thank you for your time. Have a great day!"

        audio_path = f"audio/output/goodbye_{uuid.uuid4().hex}.mp3"
        synthesize_speech(goodbye, output_path=audio_path)

        return jsonify({
            "question": goodbye,
            "audio": encode_audio_base64(audio_path),
            "ended": True
        })

    question = interview_manager.next_question(user_text)
    print(f"ARAI: {question}")

    audio_path = f"audio/output/question_{uuid.uuid4().hex}.mp3"
    synthesize_speech(question, output_path=audio_path)

    return jsonify({
        "question": question,
        "audio": encode_audio_base64(audio_path),
        "ended": False
    })

# ------------------------
# Entry Point
# ------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("🎭 AR VIRTUAL INTERVIEWER - Backend Server")
    print("=" * 60)
    print("\n📱 Access from laptop:")
    print("   http://127.0.0.1:5000")
    print("\n📱 Access from phone (same WiFi):")
    print("   http://<YOUR_IP>:5000")
    print("\n⚠️ Make sure FFmpeg is installed and in PATH")
    print("=" * 60 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
