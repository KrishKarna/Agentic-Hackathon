import os
import sys
import time
import threading

import cv2
from flask import Flask, Response, jsonify, render_template


sys.path.append(os.path.dirname(__file__))

from runtime import NavigationRuntime


app = Flask(__name__)

runtime = NavigationRuntime()

frame_lock = threading.Lock()
latest_jpeg = None
camera_error = None


def camera_loop():
    global latest_jpeg, camera_error

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        camera_error = "Could not open the camera."
        return

    runtime.start_voice_listener()

    while True:
        ret, frame = cap.read()

        if not ret:
            time.sleep(0.1)
            continue

        _, annotated_frame = runtime.process_frame(frame)

        ok, buffer = cv2.imencode(".jpg", annotated_frame)

        if ok:
            with frame_lock:
                latest_jpeg = buffer.tobytes()

        time.sleep(0.03)


def gen_frames():
    while True:
        with frame_lock:
            frame = latest_jpeg

        if frame is None:
            time.sleep(0.05)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/api/status")
def api_status():
    status = runtime.get_status()
    status["camera_error"] = camera_error

    return jsonify(status)


if __name__ == "__main__":
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
