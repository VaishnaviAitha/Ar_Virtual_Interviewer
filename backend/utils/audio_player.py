# backend/utils/audio_player.py
import simpleaudio as sa

def play_audio(audio_path: str):
    try:
        wave_obj = sa.WaveObject.from_wave_file(audio_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception:
        # Fallback for mp3 using OS player
        import os, sys
        if sys.platform == "win32":
            os.system(f'start {audio_path}')
        elif sys.platform == "darwin":
            os.system(f'afplay "{audio_path}"')
        else:
            os.system(f'mpg123 "{audio_path}"')
