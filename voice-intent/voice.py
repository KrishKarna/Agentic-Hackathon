import speech_recognition as sr


def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()

    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
        return None

    except sr.RequestError:
        print("Speech recognition service error.")
        return None


def get_intent(command):
    command = command.lower()

    if any(word in command for word in [
        "obstacle",
        "obstacles",
        "path",
        "clear"
    ]):
        return "check_obstacle", None

    if any(word in command for word in [
        "describe",
        "scene",
        "around me",
        "surroundings"
    ]):
        return "describe_scene", None

    if any(word in command for word in [
        "find",
        "look for",
        "where is",
        "locate"
    ]):
        objects = [
            "person",
            "chair",
            "cell phone",
            "phone",
            "backpack",
            "bottle",
            "cup",
            "laptop",
            "keyboard",
            "mouse",
            "book"
        ]

        for obj in objects:
            if obj in command:
                if obj == "phone":
                    obj = "cell phone"

                return "find_object", obj

    return None, None


if __name__ == "__main__":
    command = listen()

    if command:
        print("Command:", command)