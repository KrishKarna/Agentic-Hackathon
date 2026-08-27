import pyttsx3
import threading

_speak_lock = threading.Lock()


def speak(message):
    def _speak():
        with _speak_lock:
            engine = pyttsx3.init()
            engine.setProperty("rate", 170)
            engine.setProperty("volume", 1.0)
            engine.say(message)
            engine.runAndWait()
            engine.stop()

    thread = threading.Thread(target=_speak, daemon=True)   # <-- added daemon=True
    thread.start()


if __name__ == "__main__":
    speak("AI navigation system is working.")