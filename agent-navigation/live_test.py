import os
import sys
import time
import threading
import cv2

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "cv-obstacles")
    )
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "tts")
    )
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "voice-intent")
    )
)

from vision import analyze_frame
from agent import NavigationAgent
from speech import speak
from voice import listen_for_command


agent = NavigationAgent()

current_intent = "check_obstacle"
current_target = None
intent_lock = threading.Lock()


def voice_listener_loop():
    global current_intent, current_target

    while True:
        intent, target = listen_for_command()

        with intent_lock:
            current_intent = intent
            current_target = target

            if intent == "find_object" and target:
                agent.set_target(target)

            # force a fresh spoken response for this new voice command
            agent.last_scene = None
            agent.last_intent = None

        print(f"Updated intent -> {current_intent}, target: {current_target}")


voice_thread = threading.Thread(target=voice_listener_loop, daemon=True)
voice_thread.start()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    sys.exit()

window_name = "AI Navigation Assistant"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

MESSAGE_COOLDOWN = 3
last_message_time = -MESSAGE_COOLDOWN

first_frame = True

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read camera frame.")
        break

    scene, annotated_frame = analyze_frame(frame)

    current_time = time.time()

    if current_time - last_message_time >= MESSAGE_COOLDOWN:
        with intent_lock:
            intent_to_use = current_intent

        message = agent.decide(intent_to_use, scene, [])

        if message is not None:
            speak(message)
        last_message_time = current_time

    cv2.imshow(window_name, annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if not first_frame:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    first_frame = False

cap.release()
cv2.destroyAllWindows()
print("Camera closed cleanly.")
sys.exit(0)