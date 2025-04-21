import cv2
import dlib
import numpy as np

# Load dlib’s face detector and 68 landmarks model
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("model/shape_predictor_68_face_landmarks.dat")

def detect_pupil(eye_region):
    gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
    gray_eye = cv2.medianBlur(gray_eye, 5)  # Use median blur for better noise reduction
    
    # Adaptive thresholding for better pupil detection
    threshold_eye = cv2.adaptiveThreshold(gray_eye, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(threshold_eye, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        pupil_contour = max(contours, key=cv2.contourArea)
        px, py, pw, ph = cv2.boundingRect(pupil_contour)
        
        # Ensure the detected region is reasonable (not too large or small)
        if 2 < pw < 50 and 2 < ph < 50:
            return (px + pw // 2, py + ph // 2), (px, py, pw, ph)
    
    return None, None

def process_eye_movement(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    gaze_direction = "Looking Center"

    for face in faces:
        landmarks = predictor(gray, face)
        
        # Extract left and right eye landmarks
        left_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
        right_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])
        
        # Get bounding rectangles for the eyes
        left_eye_rect = cv2.boundingRect(left_eye_points)
        right_eye_rect = cv2.boundingRect(right_eye_points)
        
        # Extract eye regions
        left_eye = frame[left_eye_rect[1]:left_eye_rect[1] + left_eye_rect[3], left_eye_rect[0]:left_eye_rect[0] + left_eye_rect[2]]
        right_eye = frame[right_eye_rect[1]:right_eye_rect[1] + right_eye_rect[3], right_eye_rect[0]:right_eye_rect[0] + right_eye_rect[2]]
        
        # Detect pupils
        left_pupil, left_bbox = detect_pupil(left_eye)
        right_pupil, right_bbox = detect_pupil(right_eye)
        
        # Draw bounding boxes and pupils
        cv2.rectangle(frame, (left_eye_rect[0], left_eye_rect[1]), 
                      (left_eye_rect[0] + left_eye_rect[2], left_eye_rect[1] + left_eye_rect[3]), (0, 255, 0), 2)
        cv2.rectangle(frame, (right_eye_rect[0], right_eye_rect[1]), 
                      (right_eye_rect[0] + right_eye_rect[2], right_eye_rect[1] + right_eye_rect[3]), (0, 255, 0), 2)
        
        if left_pupil and left_bbox:
            cv2.circle(frame, (left_eye_rect[0] + left_pupil[0], left_eye_rect[1] + left_pupil[1]), 5, (0, 0, 255), -1)
        if right_pupil and right_bbox:
            cv2.circle(frame, (right_eye_rect[0] + right_pupil[0], right_eye_rect[1] + right_pupil[1]), 5, (0, 0, 255), -1)
        
        # Gaze Detection
        if left_pupil and right_pupil:
            lx, ly = left_pupil
            rx, ry = right_pupil
            
            eye_width = left_eye_rect[2]
            
            # Normalize pupil position
            lx_norm, rx_norm = lx / eye_width, rx / eye_width
            
            if lx_norm < 0.3 and rx_norm < 0.3:
                gaze_direction = "Looking Left"
            elif lx_norm > 0.7 and rx_norm > 0.7:
                gaze_direction = "Looking Right"
            elif ly < left_eye_rect[3] // 3 and ry < right_eye_rect[3] // 3:
                gaze_direction = "Looking Up"
            elif ly > 2 * left_eye_rect[3] // 3 and ry > 2 * right_eye_rect[3] // 3:
                gaze_direction = "Looking Down"
            else:
                gaze_direction = "Looking Center"
    
    return frame, gaze_direction
