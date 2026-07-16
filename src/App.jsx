import React, { useState, useEffect, useRef } from 'react';
import Globe from 'react-globe.gl';
import { 
  Activity, Brain, Cloud, Database, 
  Map, Navigation, Radio, Satellite, 
  ShieldAlert, Smartphone, Zap, 
  Settings, Layers, List, Camera
} from 'lucide-react';

const DigitalTwinDashboard = () => {
  const [inspections, setInspections] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeTab, setActiveTab] = useState('telemetry');
  const [aiConfidence, setAiConfidence] = useState(85);
  const globeRef = useRef();
  const wsRef = useRef(null);

  // Initial Fetch & WebSocket Setup
  useEffect(() => {
    fetchInitialData();
    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      const response = await fetch('http://localhost:8000/inspections/');
      if (response.ok) {
        const data = await response.json();
        setInspections(data.reverse()); // Newest first
      }
    } catch (error) {
      console.error("API Connection Error", error);
    }
  };

  const connectWebSocket = () => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws');
    
    wsRef.current.onmessage = (event) => {
      const newDefect = JSON.parse(event.data);
      
      // Prepend the new live data point to the state
      setInspections(prev => {
        // Keep array manageable (max 100 items)
        const updated = [newDefect, ...prev];
        if (updated.length > 100) updated.pop();
        return updated;
      });

      // Animate Globe to the live event if it's high severity
      if (newDefect.severity > 70 && globeRef.current) {
        globeRef.current.pointOfView({ 
          lat: newDefect.latitude, 
          lng: newDefect.longitude, 
          altitude: 1.5 
        }, 1500);
      }
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected. Reconnecting...');
      setTimeout(connectWebSocket, 3000);
    };
  };

  const simulateUpload = async () => {
    setIsSimulating(true);
    try {
      const mockResponse = await fetch('http://localhost:8000/mock_upload/', { method: 'POST' });
      const mockData = await mockResponse.json();
      
      const formData = new FormData();
      formData.append('latitude', mockData.latitude);
      formData.append('longitude', mockData.longitude);
      
      const dummyBlob = new Blob(['mock image data'], { type: 'image/jpeg' });
      formData.append('file', dummyBlob, mockData.filename);

      // We don't need to manually update state here, the WebSocket will catch the broadcast!
      await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });

    } catch (error) {
      console.error("Simulation failed", error);
    } finally {
      setIsSimulating(false);
    }
  };

  const globeData = inspections.map(insp => ({
    lat: insp.latitude,
    lng: insp.longitude,
    weight: insp.severity / 100,
    color: insp.severity > 70 ? '#ef4444' : insp.severity > 40 ? '#f59e0b' : '#10b981',
    label: `${insp.defect_type} (Sev: ${insp.severity.toFixed(0)})`
  }));

  return (
    <div className="dashboard-container">
      {/* FULLSCREEN BACKGROUND GLOBE */}
      <div className="globe-background">
        <Globe
          ref={globeRef}
          globeImageUrl="//unpkg.com/three-globe/example/img/earth-dark.jpg"
          bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
          backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
          pointsData={globeData}
          pointAltitude="weight"
          pointColor="color"
          pointRadius={0.5}
          pointsMerge={true}
          labelsData={globeData}
          labelDotRadius={0.5}
          labelColor={() => 'rgba(255, 255, 255, 0.75)'}
          labelText="label"
          labelSize={1.5}
          labelResolution={2}
          labelAltitude={d => d.weight + 0.05}
          atmosphereColor="#06b6d4"
          atmosphereAltitude={0.15}
        />
      </div>

      {/* TOP NAVIGATION BAR */}
      <nav className="glass-nav">
        <div className="nav-brand">
          <Database className="icon-cyan" />
          <h1>INFRA-AI <span className="subtitle">OS</span></h1>
        </div>
        <div className="nav-controls">
          <div className="status-badge">
            <span className="pulse-dot"></span>
            Live Digital Twin (WebSocket)
          </div>
          <button 
            className={`btn-simulate ${isSimulating ? 'simulating' : ''}`}
            onClick={simulateUpload}
            disabled={isSimulating}
          >
            {isSimulating ? <Activity className="spin" /> : <Satellite />}
            {isSimulating ? 'Analyzing via AI...' : 'Manual Drone Upload'}
          </button>
        </div>
      </nav>

      {/* LEFT SIDEBAR: CONTROLS & SETTINGS */}
      <aside className="glass-sidebar left-sidebar">
        <div className="sidebar-header">
          <Settings className="icon" />
          <h2>Parameters</h2>
        </div>
        
        <div className="control-group">
          <label>AI Confidence Threshold: {aiConfidence}%</label>
          <input 
            type="range" 
            min="50" max="99" 
            value={aiConfidence} 
            onChange={(e) => setAiConfidence(e.target.value)}
            className="slider"
          />
        </div>

        <div className="control-group">
          <h3><Layers className="icon-small" /> Map Layers</h3>
          <div className="toggle-row">
            <span>Structural Meshes (BIM)</span>
            <div className="toggle active"></div>
          </div>
          <div className="toggle-row">
            <span>Live Drone Paths</span>
            <div className="toggle active"></div>
          </div>
          <div className="toggle-row">
            <span>IoT Sensor Overlay</span>
            <div className="toggle active"></div>
          </div>
        </div>

        <div className="control-group">
          <h3><Brain className="icon-small" /> AI Modules</h3>
          <div className="module-badge active">Pothole Detection (YOLO)</div>
          <div className="module-badge active">Crack Detection (ResNet)</div>
          <div className="module-badge">Corrosion (Pending)</div>
        </div>
        
        <div className="colormap-legend">
          <h4>Severity Heatmap</h4>
          <div className="gradient-bar"></div>
          <div className="legend-labels">
            <span>Safe (0%)</span>
            <span>Critical (100%)</span>
          </div>
        </div>
      </aside>

      {/* RIGHT SIDEBAR: LIVE TELEMETRY */}
      <aside className="glass-sidebar right-sidebar">
        <div className="sidebar-tabs">
          <button 
            className={activeTab === 'telemetry' ? 'active' : ''} 
            onClick={() => setActiveTab('telemetry')}
          >
            <Radio className="icon-small" /> Telemetry
          </button>
          <button 
            className={activeTab === 'inspections' ? 'active' : ''} 
            onClick={() => setActiveTab('inspections')}
          >
            <List className="icon-small" /> History
          </button>
        </div>

        <div className="sidebar-content">
          {activeTab === 'telemetry' ? (
            <div className="telemetry-feed">
              <div className="log-entry system">
                <span className="time">{new Date().toLocaleTimeString()}</span>
                <span className="msg">WebSocket Connected. Streaming real-time telemetry...</span>
              </div>
              {inspections.slice(0, 15).map((insp, i) => (
                <div key={i} className={`log-entry ${insp.severity > 70 ? 'alert' : 'info'} animate-in`}>
                  <span className="time">{new Date(insp.created_at || Date.now()).toLocaleTimeString()}</span>
                  <span className="msg">
                    <strong>[{insp.id ? `ID:${insp.id}` : 'DRONE-AI'}]</strong> Detected {insp.defect_type}. 
                    Sev: {insp.severity.toFixed(1)}. Lat: {insp.latitude.toFixed(4)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="inspection-list">
              {inspections.filter(i => i.id).map((insp) => (
                <div key={insp.id} className="inspection-card">
                  <div className="card-header">
                    <span className="defect-type">{insp.defect_type}</span>
                    <span className={`severity-badge ${insp.severity > 70 ? 'high' : insp.severity > 40 ? 'med' : 'low'}`}>
                      {insp.severity.toFixed(0)}%
                    </span>
                  </div>
                  <div className="card-body">
                    <img 
                      src={insp.image_url.startsWith('http') ? insp.image_url : `http://localhost:8000${insp.image_url}`} 
                      alt="Defect" 
                      onError={(e) => { e.target.src = 'https://via.placeholder.com/300x200?text=AI+Processed+Image' }}
                    />
                    <div className="meta">
                      <span><Map className="icon-xs" /> {insp.latitude.toFixed(4)}, {insp.longitude.toFixed(4)}</span>
                    </div>
                  </div>
                </div>
              ))}
              {inspections.length === 0 && (
                <div className="empty-state">
                  <Camera className="icon-large" />
                  <p>No field data yet.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
};

export default DigitalTwinDashboard;
