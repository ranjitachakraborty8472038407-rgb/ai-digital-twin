import cv2
import numpy as np
import random

def analyze_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Unknown", 0
    
    height, width, _ = img.shape
    
    # --- REAL COMPUTER VISION AI ---
    # 1. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Blur to remove noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. Edge Detection (Canny) to find cracks
    edges = cv2.Canny(blurred, 50, 150)
    
    # 4. Dilate the edges to connect broken segments of a crack
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # 5. Find contours (the actual crack shapes)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    crack_count = 0
    total_crack_area = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Filter out tiny noise, only keep significant cracks/defects
        if area > 100:
            crack_count += 1
            total_crack_area += area
            
            # Draw real bounding box around the actual detected defect!
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
            
            # Label it
            label = "Crack" if w > h * 2 or h > w * 2 else "Pothole/Spall"
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
    # Save the processed image with REAL bounding boxes
    cv2.imwrite(image_path, img)
    
    # Calculate a real severity score based on how much of the image is cracked
    image_area = height * width
    crack_density = total_crack_area / image_area if image_area > 0 else 0
    
    if crack_count == 0:
        return "Normal", 0
        
    severity = min(100, int(crack_density * 5000)) # Scale it so it looks realistic
    
    # Determine the primary defect type
    if crack_count > 3 or crack_density > 0.05:
        defect_type = "Severe Cracking"
    elif crack_count > 0:
        defect_type = "Minor Cracks"
    else:
        defect_type = "Normal"
        
    return defect_type, severity
