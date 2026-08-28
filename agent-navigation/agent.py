import os
import json
from dotenv import load_dotenv
from groq import Groq


project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

load_dotenv(
    os.path.join(project_root, ".env")
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY not found in .env file"
    )


client = Groq(api_key=api_key)


class NavigationAgent:

    def __init__(self):
        self.last_scene = None
        self.last_intent = None
        self.target_object = None
        self.last_target_state = None
        self.target_was_visible = False

    def set_target(self, object_name):
        self.target_object = object_name.lower()
        self.last_target_state = None
        self.target_was_visible = False
        self.last_scene = None

    def reset_target(self):
        self.target_object = None
        self.last_target_state = None
        self.target_was_visible = False
        self.last_scene = None
        self.last_intent = None

    def decide(self, intent, scene, text):

        if intent == "find_object":
            return self._find_object(scene)

        return self._handle_general_intent(
            intent,
            scene,
            text
        )

    def _find_object(self, scene):

        if not self.target_object:
            return None

        matches = []

        for obj in scene:
            if (
                obj.get("object")
                == self.target_object
            ):
                matches.append(obj)

        if not matches:

            if self.target_was_visible:

                self.target_was_visible = False
                self.last_target_state = "not_visible"

                return (
                    f"I cannot see the "
                    f"{self.target_object} anymore."
                )

            return None


        target = matches[0]

        position = target.get(
            "position",
            "center"
        )

        distance = target.get(
            "distance",
            "unknown"
        )


        current_target_state = json.dumps(
            {
                "position": position,
                "distance": distance
            },
            sort_keys=True
        )


        if (
            current_target_state
            == self.last_target_state
        ):
            return None


        self.target_was_visible = True
        self.last_target_state = (
            current_target_state
        )


        if distance == "near":

            return (
                f"You are close to the "
                f"{self.target_object}."
            )


        return (
            f"{self.target_object.capitalize()} "
            f"on your {position}, "
            f"{distance} away."
        )

    def _handle_general_intent(
        self,
        intent,
        scene,
        text
    ):

        scene_state = {
            "intent": intent,
            "scene": scene,
            "text": text
        }

        current_state = json.dumps(
            scene_state,
            sort_keys=True
        )

        if (
            current_state == self.last_scene
            and intent == self.last_intent
        ):
            return None

        self.last_scene = current_state
        self.last_intent = intent

        return self._ask_llm(
            intent,
            scene,
            text
        )

    def _ask_llm(
        self,
        intent,
        scene,
        text
    ):

        prompt = f"""
You are a navigation assistant helping
a visually impaired person.

User intent: {intent}

Detected objects:
{scene}

Detected text:
{text}

Give one short, clear spoken navigation instruction.

Rules:
- Keep it under 20 words.
- Focus on the user's intent.
- Prioritize nearby obstacles.
- Do not explain your reasoning.
- Return only the instruction.
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )