import os
import sys
import cv2


sys.path.append(os.path.dirname(__file__))

from runtime import NavigationRuntime
from speech import speak


print("AI Navigation Assistant started.")
print("Please say a command.")


runtime = NavigationRuntime()
runtime.start_voice_listener()


cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("Error: Could not open camera.")
    speak("I could not open the camera.")
    sys.exit()


window_name = "AI Navigation Assistant"

cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL
)


print("\nSay a new command anytime to search for something else.")
print("Press 'q' to quit.\n")


while True:

    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read camera frame.")
        break

    _, annotated_frame = runtime.process_frame(frame)

    cv2.imshow(window_name, annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if (
        cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
        < 1
    ):
        break


cap.release()

cv2.destroyAllWindows()
