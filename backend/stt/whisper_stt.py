# backend/stt/whisper_stt.py
import whisper

_model = None

def _load_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(audio_path: str) -> str:
    model = _load_model()
    result = model.transcribe(audio_path)
    return result.get("text", "").strip()
