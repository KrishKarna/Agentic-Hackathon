import os
import speech_recognition as sr
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def listen():
    recognizer = sr.Recognizer()

    while True:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            try:
                audio = recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=7
                )
            except sr.WaitTimeoutError:
                print("No speech detected. Try again.")
                continue

        try:
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            return text

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that. Please try again.")

        except sr.RequestError:
            print("Speech recognition service error.")
            return None


def get_intent(command):
    """
    Uses an LLM to interpret the spoken command into one of the known intents.
    """
    valid_objects = [
        "person", "chair", "cell phone", "backpack",
        "bottle", "cup", "laptop", "keyboard", "mouse", "book"
    ]

    prompt = f"""You are an intent classifier for a navigation assistant for visually impaired users.

The user said: "{command}"

Classify this into exactly ONE of these intents:
- check_obstacle (user wants to know about obstacles/path ahead)
- describe_scene (user wants a general description of surroundings)
- read_sign (user wants text/signs read aloud)
- find_object (user wants to locate a specific object)

If the intent is find_object, also identify the target object from this list only: {valid_objects}
If no object from the list matches, use find_object with target "none".

Respond in EXACTLY this format, nothing else:
intent: <intent_name>
target: <object_name_or_none>"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip().lower()

        intent = None
        target = None

        for line in result.splitlines():
            if line.startswith("intent:"):
                intent = line.split(":", 1)[1].strip()
            elif line.startswith("target:"):
                target = line.split(":", 1)[1].strip()
                if target == "none":
                    target = None

        valid_intents = ["check_obstacle", "describe_scene", "read_sign", "find_object"]
        if intent not in valid_intents:
            return None, None

        return intent, target

    except Exception as e:
        print(f"Intent classification error: {e}")
        return None, None


def listen_for_command():
    while True:
        command = listen()

        if not command:
            continue

        intent, target = get_intent(command)

        if intent is not None:
            return intent, target

        print("Command not understood. Please try again.")


if __name__ == "__main__":
    intent, target = listen_for_command()
    print("Intent:", intent)
    print("Target:", target)