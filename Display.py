#WE WILL RECIEVE ALERTS IN THIS CODE

import socket
import cv2
import numpy as np
import threading
import platform
import os
from datetime import datetime

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 9999
SAVE_DIR = "received_overspeed_frames"

# Create directory if not exists
os.makedirs(SAVE_DIR, exist_ok=True)

def beep_sound():
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 500)
        else:
            print("\a")
    except Exception as e:
        print(f"Beep failed: {e}")

def handle_client(conn, addr, client_id):
    try:
        print(f"[Client {client_id}] Connected from {addr}")
        data = b""
        while b"<ENDMSG>" not in data:
            part = conn.recv(1024)
            if not part:
                break
            data += part

        message, remainder = data.split(b"<ENDMSG>", 1)
        alert_message = message.decode()
        print(f"[Client {client_id}] Alert message: {alert_message}")

        # Receive image bytes
        image_data = remainder
        while b"<ENDIMG>" not in image_data:
            part = conn.recv(4096)
            if not part:
                break
            image_data += part

        image_data = image_data.split(b"<ENDIMG>")[0]
        img_array = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if frame is not None:
            # Save frame with timestamp and client ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{SAVE_DIR}/alert_{client_id}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)

            # Display frame in a window
            window_name = f"Alert from {addr[0]} (Client {client_id})"
            cv2.imshow(window_name, frame)
            cv2.waitKey(1)  # Allow OpenCV to process UI events

        beep_sound()

    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")
    finally:
        conn.close()

def receive_alerts():
    print(f"Listening for alerts on {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        client_id = 0
        while True:
            conn, addr = s.accept()
            client_id += 1
            threading.Thread(target=handle_client, args=(conn, addr, client_id), daemon=True).start()

if __name__ == "__main__":
    receive_alerts()
