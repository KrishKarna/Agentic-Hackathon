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

        position = get_position(x_center, width)
        distance = get_distance(box_area, frame_area)

        scene.append({
            "object": label,
            "position": position,
            "distance": distance
        })

    annotated_frame = results.plot()

    return scene, annotated_frame