# backend/utils/audio_recorder.py
import sounddevice as sd
from scipy.io.wavfile import write
import os

def record_audio(output_path: str, duration: int = 6, fs: int = 16000):
    print(f"🎙️ Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    write(output_path, fs, recording)
    print("✅ Recording saved.")
