import pyttsx3
import threading
import queue


speech_queue = queue.Queue()


def speech_worker():

    engine = pyttsx3.init()

    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    while True:

        message = speech_queue.get()

        if message is None:
            break

        engine.say(message)

        engine.runAndWait()

        speech_queue.task_done()


worker = threading.Thread(
    target=speech_worker,
    daemon=True
)

worker.start()


def speak(message):

    if message:
        speech_queue.put(message)


if __name__ == "__main__":

    speak("AI navigation system is working.")

    speech_queue.join()