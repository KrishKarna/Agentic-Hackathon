import os
import sys
import time
import cv2
import threading


project_root = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)


sys.path.append(
    os.path.join(
        project_root,
        "cv-obstacles"
    )
)

sys.path.append(
    os.path.join(
        project_root,
        "tts"
    )
)

sys.path.append(
    os.path.join(
        project_root,
        "voice-intent"
    )
)


from vision import analyze_frame
from agent import NavigationAgent
from speech import speak
from voice import listen_for_command
from safety import check_emergency


print("AI Navigation Assistant started.")
print("Please say a command.")


intent, target = listen_for_command()


print("Intent:", intent)

if target:
    print("Target:", target)


agent = NavigationAgent()


if intent == "find_object":
    agent.set_target(target)


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


MESSAGE_COOLDOWN = 3
EMERGENCY_COOLDOWN = 2


last_message_time = 0
last_emergency_time = 0

last_emergency_message = None

agent_busy = False


def get_agent_response(
    current_scene
):

    global agent_busy

    try:

        message = agent.decide(
            intent,
            current_scene,
            []
        )

        if message:
            speak(message)

    finally:

        agent_busy = False


while True:

    ret, frame = cap.read()


    if not ret:
        print("Error: Could not read camera frame.")
        break


    scene, annotated_frame = analyze_frame(
        frame
    )


    current_time = time.time()


    emergency_message = check_emergency(
        scene
    )


    if emergency_message:

        emergency_changed = (
            emergency_message
            != last_emergency_message
        )


        if (
            emergency_changed
            or current_time
            - last_emergency_time
            >= EMERGENCY_COOLDOWN
        ):

            speak(emergency_message)

            last_emergency_time = current_time

            last_emergency_message = (
                emergency_message
            )


    else:

        last_emergency_message = None


        if (
            not agent_busy
            and current_time
            - last_message_time
            >= MESSAGE_COOLDOWN
        ):

            agent_busy = True

            last_message_time = current_time


            agent_thread = threading.Thread(
                target=get_agent_response,
                args=(scene.copy(),),
                daemon=True
            )

            agent_thread.start()


    cv2.imshow(
        window_name,
        annotated_frame
    )


    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):
        break


    if (
        cv2.getWindowProperty(
            window_name,
            cv2.WND_PROP_VISIBLE
        )
        < 1
    ):
        break


cap.release()

cv2.destroyAllWindows()