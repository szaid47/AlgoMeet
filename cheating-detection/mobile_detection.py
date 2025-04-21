import cv2
import torch
from ultralytics import YOLO

# Load trained YOLOv8m model
model = YOLO("model/best.pt")  # Ensure correct model path
device = "cuda" if torch.cuda.is_available() else "cpu"

def process_mobile_detection(frame):
    results = model(frame, verbose=False)
    mobile_detected = False

    for result in results:
        boxes = result.boxes  # Extract bounding boxes

        for box in boxes:
            conf = float(box.conf[0])  # Confidence score
            cls = int(box.cls[0])  # Class index

            # Ensure correct mobile class index (adjust if needed)
            if conf < 0.8 or cls != 0:
                continue

            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            label = f"Mobile ({conf:.2f})"

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            mobile_detected = True

    return frame, mobile_detected

def run_webcam():
    cap = cv2.VideoCapture(0)  # Use 1 if external webcam

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not access webcam!")
            break

        frame, _ = process_mobile_detection(frame)  # Detect objects
        cv2.imshow("Live Mobile Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
