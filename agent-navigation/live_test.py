import os
import sys
import time
import cv2

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(
    os.path.join(project_root, "cv-obstacles")
)

sys.path.append(
    os.path.join(project_root, "tts")
)

sys.path.append(
    os.path.join(project_root, "voice-intent")
)

from vision import analyze_frame
from agent import NavigationAgent
from speech import speak
from voice import listen, get_intent


print("AI Navigation Assistant started.")
print("Please say a command.")

command = listen()

if not command:
    print("No command detected.")
    speak("I could not hear your command.")
    sys.exit()

print("You said:", command)

intent, target = get_intent(command)

if intent is None:
    print("Command not understood.")
    speak("I could not understand the command.")
    sys.exit()

print("Intent:", intent)

agent = NavigationAgent()

if intent == "find_object":
    agent.set_target(target)

print("Opening camera...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    speak("I could not open the camera.")
    sys.exit()

window_name = "AI Navigation Assistant"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

MESSAGE_COOLDOWN = 3
last_message_time = 0


while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read camera frame.")
        break

    scene, annotated_frame = analyze_frame(frame)

    current_time = time.time()

    if current_time - last_message_time >= MESSAGE_COOLDOWN:

        message = agent.decide(intent, scene, [])

        if message is not None:
            speak(message)

        last_message_time = current_time

    cv2.imshow(window_name, annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if cv2.getWindowProperty(
        window_name,
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break

cap.release()
cv2.destroyAllWindows()