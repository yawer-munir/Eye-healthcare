import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Set up the face mesh model
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Helper function to calculate Euclidean distance between two points
def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Calculate EAR for a set of eye landmarks
def calculate_ear(eye_landmarks):
    A = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    B = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    C = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
    return (A + B) / (2.0 * C)

# Initialize variables for blink detection
blink_counter = 0
eye_closed_frame_counter = 0
eye_closed_threshold = 3  # Number of consecutive frames with EAR below threshold to count as a blink
ear_threshold = 0.2  # Threshold for EAR to indicate eye is closed

# Timing variables
start_time = time.time()
elapsed_time = 0

# Initialize video capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the image to find facial landmarks
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            eye_landmarks = []
            
            # Approximate indices for the left eye
            left_eye_indices = [33, 160, 158, 133, 153, 144]
            # Approximate indices for the right eye
            right_eye_indices = [362, 385, 386, 263, 373, 380]

            # Get the landmarks for the left eye
            for idx in left_eye_indices:
                x, y = int(landmarks.landmark[idx].x * w), int(landmarks.landmark[idx].y * h)
                eye_landmarks.append((x, y))

            # Calculate EAR for the left eye
            left_ear = calculate_ear(eye_landmarks)
            
            # Get the landmarks for the right eye
            eye_landmarks = []
            for idx in right_eye_indices:
                x, y = int(landmarks.landmark[idx].x * w), int(landmarks.landmark[idx].y * h)
                eye_landmarks.append((x, y))

            # Calculate EAR for the right eye
            right_ear = calculate_ear(eye_landmarks)

            # Determine if eyes are closed
            if left_ear < ear_threshold and right_ear < ear_threshold:
                eye_closed_frame_counter += 1
            else:
                if eye_closed_frame_counter >= eye_closed_threshold:
                    blink_counter += 1
                eye_closed_frame_counter = 0

    # Calculate blink rate per minute
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time >= 10:
        blink_rate = blink_counter
        # Reset the counters
        blink_counter = 0
        start_time = current_time
        
        # Print recommendations based on blink rate
        if blink_rate < 33:
            recommendation = "take eye drops and break to reduce eye strain."
        elif 33 <= blink_rate <= 45:
            recommendation = " take a break, wash eyes, drink water, relax."
        elif blink_rate > 55:
            recommendation = "visit to doctor."
        else:
            recommendation = "Blink rate data is not available."
        
        cv2.putText(frame, f"Blink Rate: {blink_rate} per minute", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, recommendation, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        print("recommendation : ",recommendation)
    # Display the resulting frame
    cv2.imshow('Eye Blink Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
