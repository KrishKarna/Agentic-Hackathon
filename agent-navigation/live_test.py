import os
import sys
import cv2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cv-obstacles")))

from vision import analyze_frame

from agent import NavigationAgent


agent = NavigationAgent()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    sys.exit()

window_name = "AI Navigation Assistant"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

current_intent = "find_seat"

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read camera frame.")
        break

    scene, annotated_frame = analyze_frame(frame)

    message = agent.decide(current_intent, scene, [])

    if message:
        print(message)

    cv2.imshow(window_name, annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
