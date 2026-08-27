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


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()


while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read camera.")
        break

    height, width, _ = frame.shape
    frame_area = width * height

    results = model(frame, verbose=False)[0]

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        x1, y1, x2, y2 = box.xyxy[0]

        x_center = float((x1 + x2) / 2)
        box_area = float((x2 - x1) * (y2 - y1))

        position = get_position(x_center, width)
        distance = get_distance(box_area, frame_area)

        message = (
            f"Detected {label} "
            f"on your {position}, "
            f"{distance} away."
        )

        print(message)

    annotated_frame = results.plot()

    cv2.imshow("YOLO Vision", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    if cv2.getWindowProperty("YOLO Vision", cv2.WND_PROP_VISIBLE) < 1:
        break


cap.release()
cv2.destroyAllWindows()
