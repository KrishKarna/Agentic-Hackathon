import os
from dotenv import load_dotenv
from groq import Groq

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

load_dotenv(os.path.join(project_root, ".env"))

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)


class NavigationAgent:
    def __init__(self):
        self.last_message = None
        self.target_object = None

    def set_target(self, object_name):
        self.target_object = object_name.lower()
        self.last_message = None

    def reset_target(self):
        self.target_object = None
        self.last_message = None

    def decide(self, intent, scene, text):
        message = self._ask_llm(intent, scene, text)

        if message == self.last_message:
            return None

        self.last_message = message
        return message

    def _ask_llm(self, intent, scene, text):
        prompt = f"""You are a navigation assistant helping a visually impaired person understand their surroundings.

User's intent: {intent}
Target object: {self.target_object}
Detected objects: {scene}
Detected text: {text}

Give ONE short, clear, spoken-style navigation instruction.
If nothing relevant is detected, say so briefly.
Keep it under 20 words.
Do not explain your reasoning.
Only return the instruction."""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    agent = NavigationAgent()

    scene = [
        {
            "object": "person",
            "position": "center",
            "distance": "near"
        },
        {
            "object": "chair",
            "position": "left",
            "distance": "far"
        }
    ]

    agent.set_target("chair")

    print(agent.decide("find_object", scene, []))