import threading
import queue
import pythoncom
import win32com.client


speech_queue = queue.Queue()


def speech_worker():
    pythoncom.CoInitialize()

    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    while True:
        message = speech_queue.get()

        if message is None:
            break

        try:
            speaker.Speak(message)
        except Exception as e:
            print(f"[SPEECH ERROR] {e}")

        speech_queue.task_done()

    pythoncom.CoUninitialize()


worker = threading.Thread(target=speech_worker, daemon=True)
worker.start()


def speak(message):
    if message:
        speech_queue.put(message)


if __name__ == "__main__":
    speak("AI navigation system is working.")
    speech_queue.join()