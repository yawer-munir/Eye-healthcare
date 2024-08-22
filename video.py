from flask import Flask, jsonify, Response
import cv2
import mediapipe as mp
import numpy as np
import time

app = Flask(__name__)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
# Eye Aspect ratio 
def calculate_ear(eye_landmarks):
    A = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    B = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    C = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
    return (A + B) / (2.0 * C)

@app.route('/recommendation', methods=['GET'])
def get_recommendation():
    global blink_counter, eye_closed_frame_counter, start_time, recommendation

    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                eye_landmarks = []
                
                left_eye_indices = [33, 160, 158, 133, 153, 144]
                right_eye_indices = [362, 385, 386, 263, 373, 380]

                for idx in left_eye_indices:
                    x, y = int(landmarks.landmark[idx].x * w), int(landmarks.landmark[idx].y * h)
                    eye_landmarks.append((x, y))

                left_ear = calculate_ear(eye_landmarks)
                
                eye_landmarks = []
                for idx in right_eye_indices:
                    x, y = int(landmarks.landmark[idx].x * w), int(landmarks.landmark[idx].y * h)
                    eye_landmarks.append((x, y))

                right_ear = calculate_ear(eye_landmarks)

                if left_ear < ear_threshold and right_ear < ear_threshold:
                    eye_closed_frame_counter += 1
                else:
                    if eye_closed_frame_counter >= eye_closed_threshold:
                        blink_counter += 1
                    eye_closed_frame_counter = 0

        current_time = time.time()
        elapsed_time = current_time - start_time
        # blinkrate per minute
        if elapsed_time >= 60:
            blink_rate = blink_counter
            blink_counter = 0
            start_time = current_time
            
            if blink_rate < 33:
                recommendation = "Your blink rate is lower than average. Consider taking breaks to reduce eye strain."
            elif 33 <= blink_rate <= 45:
                recommendation = "Your blink rate is within the normal range. Maintain good eye health habits."
            elif blink_rate > 55:
                recommendation = "Your blink rate is higher than average. Ensure you are not experiencing eye discomfort or fatigue."
            else:
                recommendation = "Blink rate data is not available."
            
            cap.release()
            return jsonify({"recommendation": recommendation})

    cap.release()
    return jsonify({"recommendation": "Unable to process video."})

if __name__ == '__main__':
    blink_counter = 0
    eye_closed_frame_counter = 0
    eye_closed_threshold = 3
    ear_threshold = 0.2
    recommendation = ""
    start_time = time.time()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
