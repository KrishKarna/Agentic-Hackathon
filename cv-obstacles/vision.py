import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")


def get_position(x_center, frame_width):
    if x_center < frame_width / 3:
        return "left"
    elif x_center > 2 * frame_width / 3:
        return "right"
    else:
        return "center"


def get_distance(box_area, frame_area):
    ratio = box_area / frame_area
    if ratio > 0.15:
        return "near"
    elif ratio > 0.05:
        return "medium"
    else:
        return "far"


def analyze_frame(frame):
    """
    Takes a camera frame, returns (scene, annotated_frame).
    scene = list of detected objects like:
        [{"object": "chair", "position": "left", "distance": "near"}, ...]
    """
    height, width, _ = frame.shape
    frame_area = width * height

    results = model(frame, verbose=False)[0]

    scene = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        x1, y1, x2, y2 = box.xyxy[0]
        x_center = float((x1 + x2) / 2)
        box_area = float((x2 - x1) * (y2 - y1))

        scene.append({
            "object": label,
            "position": get_position(x_center, width),
            "distance": get_distance(box_area, frame_area)
        })

    annotated_frame = results.plot()
    return scene, annotated_frame


# only runs when testing vision.py directly, not when imported
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read camera.")
            break

        scene, annotated_frame = analyze_frame(frame)

        for obj in scene:
            print(f"Detected {obj['object']} on your {obj['position']}, {obj['distance']} away.")

        cv2.imshow("YOLO Vision", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("YOLO Vision", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()