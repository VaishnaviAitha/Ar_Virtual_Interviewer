import time

from llm.gemini_client import GeminiClient
from stt.whisper_stt import transcribe_audio
from tts.local_tts import synthesize_speech
from utils.audio_recorder import record_audio
from conversation.interview_manager import InterviewManager

AUDIO_INPUT_PATH = "audio/input/user.wav"

def main():
    print("🎤 ARAI Virtual Interviewer (Free Stack) starting...")

    interview_manager = InterviewManager(mode="general")

    # Model speaks first
    first_question = interview_manager.start_interview()
    print(f"\nARAI: {first_question}")
    synthesize_speech(first_question)

    # Conversation loop
    while True:
        print("\nListening to user... (speak now)")
        record_audio(AUDIO_INPUT_PATH, duration=6)

        user_text = transcribe_audio(AUDIO_INPUT_PATH)
        print(f"User: {user_text}")

        if user_text.strip().lower() in ["exit", "quit", "stop"]:
            print("Ending interview session.")
            synthesize_speech("Thank you for your time. Have a great day.")
            break

        next_question = interview_manager.next_question(user_text)
        print(f"\nARAI: {next_question}")
        synthesize_speech(next_question)

        time.sleep(0.3)

if __name__ == "__main__":
    main()
