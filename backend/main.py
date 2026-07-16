from fastapi import FastAPI, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import random
import os
import time

import models, database
import ai_worker
from database import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manage WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

# Background task to generate real-time drone data
async def drone_simulation_task():
    while True:
        await asyncio.sleep(random.uniform(2.0, 5.0)) # Generate data every 2-5 seconds
        
        # Simulate a drone finding a defect anywhere in the world
        mock_defect = {
            "id": random.randint(1000, 9999),
            "latitude": random.uniform(-90.0, 90.0),
            "longitude": random.uniform(-180.0, 180.0),
            "defect_type": random.choice(["Crack", "Pothole", "Corrosion"]),
            "severity": random.uniform(10.0, 99.9),
            "image_url": "https://via.placeholder.com/300x200?text=Live+Drone+Feed",
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
        }
        
        # Send live directly to connected dashboards
        await manager.broadcast(mock_defect)

@app.on_event("startup")
async def startup_event():
    # Database Initialization
    for i in range(5):
        try:
            models.Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
            break
        except Exception as e:
            print(f"Waiting for DB... {e}")
            time.sleep(2)
            
    # Start the live background simulator
    asyncio.create_task(drone_simulation_task())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Process with AI
    defect_type, severity = ai_worker.analyze_image(file_path)
    
    db = database.SessionLocal()
    new_inspection = models.Inspection(
        latitude=latitude,
        longitude=longitude,
        image_url=f"http://localhost:8000/uploads/{file.filename}",
        defect_type=defect_type,
        severity=severity
    )
    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)
    
    # Broadcast the real upload instantly
    inspection_dict = {
        "id": new_inspection.id,
        "latitude": new_inspection.latitude,
        "longitude": new_inspection.longitude,
        "defect_type": new_inspection.defect_type,
        "severity": new_inspection.severity,
        "image_url": new_inspection.image_url,
        "created_at": time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    }
    asyncio.create_task(manager.broadcast(inspection_dict))
    
    db.close()
    return new_inspection

@app.get("/inspections/")
def get_inspections():
    db = database.SessionLocal()
    inspections = db.query(models.Inspection).all()
    db.close()
    return inspections

@app.post("/mock_upload/")
def mock_upload():
    return {
        "latitude": random.uniform(-90.0, 90.0),
        "longitude": random.uniform(-180.0, 180.0),
        "filename": "simulated_field_image.jpg"
    }

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
