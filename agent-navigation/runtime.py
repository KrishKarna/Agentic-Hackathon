import os
import sys
import time
import threading
from collections import deque


project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(os.path.join(project_root, "cv-obstacles"))
sys.path.append(os.path.join(project_root, "tts"))
sys.path.append(os.path.join(project_root, "voice-intent"))
sys.path.append(os.path.join(project_root, "ocr-sign"))

from vision import analyze_frame
from agent import NavigationAgent
from speech import speak
from voice import listen_for_command
from safety import check_emergency
from ocr import read_sign


MESSAGE_COOLDOWN = 3
EMERGENCY_COOLDOWN = 2
HISTORY_LIMIT = 30


class NavigationRuntime:
    """Shared camera/voice/agent loop used by both the desktop (cv2) and web frontends."""

    def __init__(self):
        self.agent = NavigationAgent()

        self.state_lock = threading.Lock()

        self.current_intent = None
        self.current_target = None

        self.last_message_time = 0
        self.last_emergency_time = 0
        self.last_emergency_message = None

        self.agent_busy = False
        self.emergency_active = False

        self.history = deque(maxlen=HISTORY_LIMIT)

        self._voice_thread = None

    def log(self, kind, text):
        if not text:
            return

        with self.state_lock:
            self.history.append({
                "time": time.time(),
                "kind": kind,
                "text": text
            })

        speak(text)

    def apply_command(self, intent, target):
        if intent == "find_object":
            self.agent.set_target(target)
        else:
            self.agent.reset_target()

        with self.state_lock:
            self.current_intent = intent
            self.current_target = target
            self.last_message_time = 0

        if intent == "find_object":
            self.log("command", f"Okay, looking for the {target}.")
        else:
            self.log("command", "Okay.")

    def _voice_loop(self):
        while True:
            intent, target = listen_for_command()
            self.apply_command(intent, target)

    def start_voice_listener(self):
        if self._voice_thread is not None:
            return

        intent, target = listen_for_command()
        self.apply_command(intent, target)

        self._voice_thread = threading.Thread(
            target=self._voice_loop,
            daemon=True
        )
        self._voice_thread.start()

    def _get_agent_response(self, intent, scene, frame):
        try:
            text = read_sign(frame) if intent == "read_sign" else []

            message = self.agent.decide(intent, scene, text)

            if message:
                self.log("agent", message)

        finally:
            with self.state_lock:
                self.agent_busy = False

    def process_frame(self, frame):
        scene, annotated_frame = analyze_frame(frame)

        current_time = time.time()

        emergency_message = check_emergency(scene)

        if emergency_message:
            emergency_changed = (
                emergency_message != self.last_emergency_message
            )

            if (
                emergency_changed
                or current_time - self.last_emergency_time >= EMERGENCY_COOLDOWN
            ):
                self.log("emergency", emergency_message)

                self.last_emergency_time = current_time
                self.last_emergency_message = emergency_message

            with self.state_lock:
                self.emergency_active = True

        else:
            self.last_emergency_message = None

            with self.state_lock:
                self.emergency_active = False

            if (
                not self.agent_busy
                and current_time - self.last_message_time >= MESSAGE_COOLDOWN
            ):
                self.agent_busy = True
                self.last_message_time = current_time

                with self.state_lock:
                    active_intent = self.current_intent

                agent_thread = threading.Thread(
                    target=self._get_agent_response,
                    args=(active_intent, scene, frame.copy()),
                    daemon=True
                )
                agent_thread.start()

        return scene, annotated_frame

    def get_status(self):
        with self.state_lock:
            return {
                "intent": self.current_intent,
                "target": self.current_target,
                "emergency_active": self.emergency_active,
                "emergency_message": self.last_emergency_message,
                "history": list(self.history)
            }
