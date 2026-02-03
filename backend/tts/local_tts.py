# backend/tts/local_tts.py
# Using gTTS (Google Text-to-Speech) + pygame for playback
from gtts import gTTS
import pygame
import os
import tempfile
import time

# Initialize pygame mixer once
pygame.mixer.init()

def synthesize_speech(text: str, output_path: str = None):
    """Synthesize speech from text and play it using Google TTS."""
    print(f"🔊 Speaking: '{text[:50]}...'")
    
    try:
        # Create temporary file if no output path specified
        temp_created = False
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
            temp_created = True
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        
        # Play the audio using pygame
        pygame.mixer.music.load(output_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Clean up temporary file
        if temp_created:
            try:
                os.unlink(output_path)
            except:
                pass
        
        print("✅ Speech completed")
    except Exception as e:
        print(f"❌ Error during speech synthesis: {e}")
        import traceback
        traceback.print_exc()