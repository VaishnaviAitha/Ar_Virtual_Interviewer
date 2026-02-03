# backend/conversation/interview_manager.py
from llm.gemini_client import GeminiClient

GENERAL_START_PROMPT = """
You are ARAI, a professional virtual interviewer conducting a general interview.

Rules:
- Start the interview by greeting the candidate and asking the first question.
- Ask only one question at a time.
- Keep the tone friendly and professional.
- Do not provide answers or opinions.
- Do not mention you are an AI.
- Do not break character.

Themes:
- How the candidate is feeling
- Their thoughts on AI and technology
- Their interests and perspectives

Begin the interview now.
"""

FOLLOW_UP_TEMPLATE = """
You are ARAI, a professional virtual interviewer conducting a general interview.

Rules:
- Ask only one question.
- Keep it conversational and friendly.
- Do not provide feedback, answers, or opinions.
- Do not mention you are an AI.
- Do not break character.

Candidate response:
"{user_text}"

Ask the next appropriate follow-up question.
"""

class InterviewManager:
    def __init__(self, mode: str = "general"):
        self.client = GeminiClient()
        self.history = []

    def start_interview(self) -> str:
        question = self.client.generate(GENERAL_START_PROMPT)
        self.history.append(("ARAI", question))
        return question

    def next_question(self, user_text: str) -> str:
        self.history.append(("User", user_text))

        prompt = FOLLOW_UP_TEMPLATE.format(user_text=user_text)
        question = self.client.generate(prompt)

        self.history.append(("ARAI", question))
        return question
