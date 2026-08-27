import pyttsx3


def speak(message):
    engine = pyttsx3.init()

    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    engine.say(message)
    engine.runAndWait()
    engine.stop()


if __name__ == "__main__":
    speak("AI navigation system is working.")