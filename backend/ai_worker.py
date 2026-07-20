import cv2
import numpy as np
import random
from ultralytics import YOLO

# Load the YOLOv8 model globally so it stays in memory
# (Ensure your server has enough RAM to load this!)
try:
    model = YOLO('yolov8n.pt')
except Exception as e:
    print(f"Warning: Failed to load YOLO model: {e}")
    model = None

def analyze_image(image_path):
    if model is None:
        return "Model Error", 0
        
    img = cv2.imread(image_path)
    if img is None:
        return "Unknown", 0
    
    # Run YOLOv8 inference
    results = model(image_path)[0]
    
    # We will track the most severe object detected
    max_severity = 0
    primary_defect = "Normal"
    
    # Analyze the detected bounding boxes
    boxes = results.boxes
    if len(boxes) == 0:
        return "Normal", 0
        
    for box in boxes:
        # Get coordinates, confidence, and class
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        
        # Draw bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        # Label it with confidence
        label = f"{cls_name} {conf:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Calculate severity based on confidence and area
        area = (x2 - x1) * (y2 - y1)
        image_area = img.shape[0] * img.shape[1]
        area_ratio = area / image_area if image_area > 0 else 0
        
        # A simple severity metric: higher confidence and larger area = more severe
        severity = int(min(100, (conf * 50) + (area_ratio * 500)))
        
        if severity > max_severity:
            max_severity = severity
            # Since standard YOLOv8 doesn't have "pothole", we'll just use the detected class name (e.g. "car", "person")
            # When you train a custom model, this will automatically become "pothole" or "crack"!
            primary_defect = f"Detected: {cls_name.capitalize()}"
            
    # Save the processed image with REAL bounding boxes
    cv2.imwrite(image_path, img)
    
    return primary_defect, max_severity
