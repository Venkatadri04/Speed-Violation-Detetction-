# 🚗 Speed Violation Detection System

A real-time vehicle speed monitoring system designed to detect and report overspeeding vehicles within private campuses such as tech parks, institutions, and residential areas. The system uses YOLOv8 for object detection, ByteTrack for tracking, and OpenCV for visualization and speed estimation.

## 📌 Features

- Real-time vehicle detection and tracking
- Speed estimation using virtual reference lines
- Alerts generated for vehicles exceeding a speed threshold (e.g., 30 km/h)
- Remote alert transmission to security systems via socket communication
- Visual display with bounding boxes and speed annotations

---

## 🔧 Tech Stack

- **Language:** Python  
- **Object Detection:** YOLOv8 (Ultralytics)  
- **Tracking:** ByteTrack  
- **Visualization:** OpenCV  
- **Communication:** Python Socket Programming

---

## 📁 Project Structure
vehicle-speed-detection/
├── main.py # Main script to run detection and speed estimation
├── tracker.py # Tracking logic using ByteTrack
├── utils.py # Utility functions (e.g., speed calculation)
├── yolov8_weights/ # YOLOv8 model weights (e.g., yolov8n.pt)
├── videos/ # Input videos
├── results/ # Output annotated videos
├── requirements.txt # Python dependencies
└── README.md # Project documentation

⚙️ Customization
Speed Threshold: Modify SPEED_LIMIT = 30 in main.py

Reference Line Coordinates: Update line_a, line_b in the script

Alert Handling: Edit socket settings in main.py to match your admin machine's IP/Port


📬 Contact
If you have questions or suggestions, feel free to open an issue or reach out:

Name: Mannepalli Venkata Aakash

Email: mvrrao1970@gmail.com

LinkedIn: https://www.linkedin.com/in/aakash-mannepalli-89a4972a8/




