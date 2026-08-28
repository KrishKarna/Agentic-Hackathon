import speech_recognition as sr


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
        "surroundings",
        "what do you see"
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