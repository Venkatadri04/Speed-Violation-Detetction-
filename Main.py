import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
import pandas as pd
import socket
import threading
import os
from datetime import datetime

# =================== Configuration ======================
VIDEOS = ["Vidieo_1", "Vidieo_2"]  # Add your video file paths here
LINE_CONFIGS = [(400, 600), (400, 600)]  # (line_y1, line_y2) according to your frames in the vidieo
REAL_DISTANCE_M = 25  # Distance between lines in meters
SPEED_THRESHOLD_KMH = 30  # Speed limit
ALERT_HOST = '111.11.111.1'  # IP of the display/monitor device
ALERT_PORT = 9999
SAVE_DIR = "overspeed_frames"

# Create directory to save overspeed frames
os.makedirs(SAVE_DIR, exist_ok=True)

# =================== Alert Sender ======================
def send_alert(message, frame):
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ALERT_HOST, ALERT_PORT))
            s.sendall(message.encode() + b"<ENDMSG>")
            s.sendall(img_encoded.tobytes() + b"<ENDIMG>")
    except Exception as e:
        print(f"Alert failed: {e}")

# =================== Process Video ======================
def process_video(video_path, line_y1, line_y2, video_id):
    model = YOLO("yolov8n.pt")
    tracker = sv.ByteTrack()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    meters_per_pixel = REAL_DISTANCE_M / abs(line_y2 - line_y1)
    track_data, speed_logs = {}, []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        results = model(frame, classes=[2, 3, 5, 7])[0]
        detections = sv.Detections.from_ultralytics(results)
        tracked = tracker.update_with_detections(detections)

        for box, track_id in zip(tracked.xyxy, tracked.tracker_id):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if track_id not in track_data:
                track_data[track_id] = {
                    'prev_cy': None, 'start_line': None,
                    'start_frame': None, 'start_cy': None,
                    'counted': False
                }

            track = track_data[track_id]

            if not track['counted'] and track['prev_cy'] is not None:
                if track['start_line'] is None and track['prev_cy'] > line_y2 >= cy:
                    track['start_line'] = 'down'
                    track['start_frame'] = frame_num
                    track['start_cy'] = cy

                elif track['start_line'] == 'down' and track['prev_cy'] > line_y1 >= cy:
                    delta_f = frame_num - track['start_frame']
                    if delta_f > 0:
                        pixels = abs(cy - track['start_cy'])
                        distance = pixels * meters_per_pixel
                        speed = round((distance / (delta_f / fps)) * 3.6, 2)
                        speed_logs.append({'Track ID': track_id, 'Speed': speed, 'Direction': 'up'})
                        track['counted'] = True

                        if speed > SPEED_THRESHOLD_KMH:
                            filename = f"{SAVE_DIR}/video{video_id}_track{track_id}_up.jpg"
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.imwrite(filename, frame)
                            send_alert(f"Overspeed detected: Track {track_id} going up at {speed} km/h", frame)

                elif track['start_line'] is None and track['prev_cy'] < line_y1 <= cy:
                    track['start_line'] = 'up'
                    track['start_frame'] = frame_num
                    track['start_cy'] = cy

                elif track['start_line'] == 'up' and track['prev_cy'] < line_y2 <= cy:
                    delta_f = frame_num - track['start_frame']
                    if delta_f > 0:
                        pixels = abs(cy - track['start_cy'])
                        distance = pixels * meters_per_pixel
                        speed = round((distance / (delta_f / fps)) * 3.6, 2)
                        speed_logs.append({'Track ID': track_id, 'Speed': speed, 'Direction': 'down'})
                        track['counted'] = True

                        if speed > SPEED_THRESHOLD_KMH:
                            filename = f"{SAVE_DIR}/video{video_id}_track{track_id}_down.jpg"
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.imwrite(filename, frame)
                            send_alert(f"Overspeed detected: Track {track_id} going down at {speed} km/h", frame)

            track['prev_cy'] = cy

            label = f"ID:{track_id}"
            color = (0, 255, 0)
            recent = next((s for s in reversed(speed_logs) if s['Track ID'] == track_id), None)
            if recent:
                label += f" {recent['Speed']} km/h"
                if recent['Speed'] > SPEED_THRESHOLD_KMH:
                    color = (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Draw reference lines
        cv2.line(frame, (0, line_y1), (frame.shape[1], line_y1), (255, 0, 0), 2)
        cv2.line(frame, (0, line_y2), (frame.shape[1], line_y2), (0, 0, 255), 2)

        # cv2.imshow(f"Video {video_id}", frame)  # Commented due to threading issues
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

    cap.release()
    # cv2.destroyWindow(f"Video {video_id}")

# =================== Run All ======================
threads = []
for idx, video in enumerate(VIDEOS):
    line1, line2 = LINE_CONFIGS[idx]
    t = threading.Thread(target=process_video, args=(video, line1, line2, idx+1))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
