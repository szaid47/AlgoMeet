import cv2
import torch
from ultralytics import YOLO

# Load YOLOv8m model
model = YOLO("model/best.pt")  
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Open webcam
cap = cv2.VideoCapture(0)  # Use 1 if external webcam

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not access webcam!")
        break

    # Run YOLOv8m detection
    results = model(frame)

    # Process detections
    for result in results:
        print(f"Detected {len(result.boxes)} objects")  # Debug print

        for box in result.boxes:
            conf = float(box.conf[0])  # Confidence score
            cls = int(box.cls[0])  # Class index

            print(f"Class: {cls}, Confidence: {conf:.2f}")  # Debug print

            # Adjust this if phone is not class 0
            if conf < 0.3:  # Lowered threshold to capture more objects
                continue

            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            label = f"Class {cls} ({conf:.2f})"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show live video
    cv2.imshow("Phone Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
