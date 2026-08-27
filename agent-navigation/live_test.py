import cv2
from ultralytics import YOLO
from agent import NavigationAgent   # agent.py must be in the same folder

model = YOLO("yolov8n.pt")
agent = NavigationAgent()

def get_position(x_center, frame_width):
    if x_center < frame_width / 3:
        return "left"
    elif x_center > 2 * frame_width / 3:
        return "right"
    else:
        return "center"

def get_distance(box_area, frame_area):
    ratio = box_area / frame_area
    return "near" if ratio > 0.15 else "far"

cap = cv2.VideoCapture(0)
window_name = "Camera"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# change this to test different intents: "check_obstacle", "find_entrance", "describe_scene", etc.
current_intent = "find_seat"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    frame_area = width * height

    results = model(frame, verbose=False)[0]

    scene = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        x1, y1, x2, y2 = box.xyxy[0]
        x_center = (x1 + x2) / 2
        box_area = (x2 - x1) * (y2 - y1)

        scene.append({
            "object": label,
            "position": get_position(x_center, width),
            "distance": get_distance(box_area, frame_area)
        })

    message = agent.decide(current_intent, scene, [])
    if message:
        print(message)

    annotated_frame = results.plot()
    cv2.imshow(window_name, annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()