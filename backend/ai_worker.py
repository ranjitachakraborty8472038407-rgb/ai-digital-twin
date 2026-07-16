import cv2
import numpy as np
import random

def analyze_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Unknown", 0
    
    height, width, _ = img.shape
    
    # Simulate a bounding box
    x = int(width * 0.25)
    y = int(height * 0.25)
    w = int(width * 0.5)
    h = int(height * 0.5)
    
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
    cv2.putText(img, "Defect", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.imwrite(image_path, img)
    
    severity = random.randint(30, 95)
    defect_type = "Pothole" if severity > 70 else "Crack"
    return defect_type, severity
