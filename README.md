# AI Operating System for National Infrastructure 🚀

This is a complete end-to-end system featuring a Flutter mobile app, a React + Three.js web dashboard, and a Python (FastAPI) AI backend powered by PostgreSQL & PostGIS.

## 1. How to Start the Backend (Database & AI API)
The backend runs entirely in Docker.
1. Open Docker Desktop.
2. Open a terminal (PowerShell or Command Prompt).
3. Navigate to the project folder:
   ```bash
   cd "D:\Workspace\AI Dgital Twin"
   ```
4. Start the backend services:
   ```bash
   docker-compose up -d
   ```
*(The API will be available at `http://localhost:8000`)*

## 2. How to Start the Web Dashboard
1. Open a **new** terminal.
2. Navigate to the project folder:
   ```bash
   cd "D:\Workspace\AI Dgital Twin"
   ```
3. Start the React development server:
   ```bash
   npm run dev
   ```
4. Open your web browser and go to `http://localhost:5173`. 
5. Scroll down to the **Live Feed** section and click the **"Simulate Field Upload"** button to see the AI analyze a mock image and instantly plot it on the 3D Digital Twin globe!

## 3. How to Run the Flutter Mobile App
To use the mobile app, you need to connect it to your local network.
1. Open a terminal and run `ipconfig` to find your computer's **IPv4 Address** (e.g., `192.168.1.xxx`).
2. Open the file `D:\Workspace\AI Dgital Twin\mobile_app\lib\main.dart` in an editor (like VS Code or Notepad).
3. Go to line **117** and replace `192.168.1.100` with your actual IPv4 address:
   ```dart
   var uri = Uri.parse('http://YOUR.IP.ADDRESS.HERE:8000/upload/'); 
   ```
4. Connect your Android phone to your computer via USB (with USB Debugging enabled), or open an Android Emulator.
5. In your terminal, navigate to the mobile app folder:
   ```bash
   cd "D:\Workspace\AI Dgital Twin\mobile_app"
   ```
6. Run the app:
   ```bash
   flutter run
   ```
7. Once the app opens on your phone, point your camera at a surface, tap **Capture & Analyze**, and watch as the photo is sent to your AI backend and instantly appears on your Web Dashboard's 3D map!
