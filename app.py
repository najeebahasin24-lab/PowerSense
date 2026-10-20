"""
PowerSense - AI-Based Smart Transformer Health Monitoring System
FastAPI Backend Application with Real-Time WebSockets & ML Inference
"""

import os
import io
import csv
import json
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml_model.predictor import predictor
from database.db import (
    init_db,
    save_telemetry,
    get_latest_telemetry,
    get_telemetry_history,
    get_recent_alerts,
    clear_alerts,
    get_transformers,
    get_maintenance_records,
    add_maintenance_record,
    delete_maintenance_record,
    get_analytics_summary
)
from simulator import SensorSimulator

# Lifespan context manager (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app):
    # Startup
    init_db()
    latest = get_latest_telemetry("TR-001")
    if not latest:
        initial_sample = sim_controller.simulator.next_sample()
        await process_and_broadcast_telemetry(initial_sample, source="Initial Calibration")
    sim_controller.start()
    yield
    # Shutdown
    sim_controller.stop()

# Initialize FastAPI app
app = FastAPI(
    title="PowerSense - Smart Transformer Health Monitoring API",
    description="IoT Telemetry Ingestion, Random Forest Health Classification, and Real-Time SCADA Dashboard",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure static folder exists
os.makedirs(STATIC_DIR, exist_ok=True)

# Pydantic Schemas
class TelemetryInput(BaseModel):
    transformer_id: str = "TR-001"
    temperature: Optional[float] = Field(None, description="TEMPERATURE in Celsius")
    oil_level: float = Field(..., description="Dielectric oil level percentage (0-100%)")
    voltage: Optional[float] = Field(None, description="RMS AC supply voltage in Volts")
    current: Optional[float] = Field(None, description="Load current in Amperes")
    timestamp: Optional[str] = None
    sensor_status: Optional[Dict[str, bool]] = None

class RuntimeModeInput(BaseModel):
    mode: str

class ScenarioInput(BaseModel):
    scenario: str = Field(..., description="NORMAL, WARNING_THERMAL, CRITICAL_LEAK, CRITICAL_OVERLOAD")

class MaintenanceInput(BaseModel):
    transformer_id: str = "TR-001"
    activity_type: str
    technician: str
    parameter_impacted: str
    findings: str

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()
last_hardware_telemetry: Optional[dict] = None

# Background Simulation Controller
class SimulationController:
    def __init__(self):
        self.simulator = SensorSimulator()
        self.is_running = True
        self.interval = 2.0  # seconds
        self.task: Optional[asyncio.Task] = None

    async def run_loop(self):
        while True:
            if self.is_running:
                try:
                    sample = self.simulator.next_sample()
                    await process_and_broadcast_telemetry(sample, source="Simulation Stream")
                except Exception as e:
                    print(f"[Sim Error] {e}")
            await asyncio.sleep(self.interval)

    def start(self):
        self.is_running = True
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_loop())

    def stop(self):
        self.is_running = False

sim_controller = SimulationController()

# Telemetry Processing & ML Inference Pipeline
async def process_and_broadcast_telemetry(payload: dict, source: str = "Hardware ESP32"):
    global last_hardware_telemetry
    transformer_id = payload.get("transformer_id", "TR-001")
    temp = float(payload.get("temperature", 0.0))
    oil = float(payload["oil_level"])
    volt = float(payload.get("voltage", 0.0))
    curr = float(payload.get("current", 0.0))
    timestamp = payload.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. AI/ML Inference via Random Forest Classifier
    ml_res = predictor.predict(
        temperature=temp,
        oil_level=oil,
        voltage=volt,
        current=curr
    )

    # 2. Package telemetry record
    record = {
        "transformer_id": transformer_id,
        "timestamp": timestamp,
        "temperature": temp,
        "oil_level": oil,
        "voltage": volt,
        "current": curr,
        "apparent_power": ml_res["apparent_power"],
        "thermal_stress_index": ml_res["thermal_stress_index"],
        "health_status": ml_res["status"],
        "confidence": ml_res["confidence"],
        "probabilities": ml_res["probabilities"],
        "risk_factors": ml_res["risk_factors"],
        "recommendations": ml_res["recommendations"],
        "alerts": ml_res["alerts"],
        "source": source
    }

    if source.startswith("ESP32") or source == "Hardware ESP32":
        last_hardware_telemetry = {
            "timestamp": timestamp,
            "sensor_status": payload.get("sensor_status") or {
                "temperature": payload.get("temperature") is not None,
                "oil_level": payload.get("oil_level") is not None,
                "voltage": payload.get("voltage") is not None,
                "current": payload.get("current") is not None
            }
        }

    # 3. Save to SQLite database
    db_id = save_telemetry(record)
    record["id"] = db_id

    # 4. Broadcast to all active WebSocket UI dashboards
    await ws_manager.broadcast({
        "type": "TELEMETRY_UPDATE",
        "data": record
    })

    return record

@app.on_event("startup")
async def startup_event():
    init_db()
    # Seed an initial normal baseline telemetry if empty
    latest = get_latest_telemetry("TR-001")
    if not latest:
        initial_sample = sim_controller.simulator.next_sample()
        await process_and_broadcast_telemetry(initial_sample, source="Initial Calibration")
    # Start simulation loop in background
    sim_controller.start()

# REST Endpoints

@app.post("/api/telemetry", summary="ESP32 Ingestion Endpoint")
async def ingest_telemetry(data: TelemetryInput):
    """
    Called by ESP32 microcontroller or external IoT devices via HTTP POST.
    Processes the raw sensor data through the Random Forest Classifier,
    persists in the SQLite database, and streams to web dashboards in real time.
    """
    record = await process_and_broadcast_telemetry(data.dict(), source="ESP32 Hardware")
    return {
        "status": "success",
        "health_status": record["health_status"],
        "confidence": record["confidence"],
        "alerts_count": len(record["alerts"]),
        "timestamp": record["timestamp"]
    }

@app.get("/api/telemetry/status")
def get_telemetry_status():
    """Returns ESP32 freshness and the availability of each reported sensor."""
    if not last_hardware_telemetry:
        return {"connected": False, "last_seen": None, "sensors": {
            "temperature": False, "oil_level": False, "voltage": False, "current": False
        }}

    try:
        last_seen = datetime.strptime(last_hardware_telemetry["timestamp"], "%Y-%m-%d %H:%M:%S")
        age_seconds = max(0, (datetime.now() - last_seen).total_seconds())
    except (KeyError, TypeError, ValueError):
        age_seconds = 999999

    connected = age_seconds <= 10
    sensors = last_hardware_telemetry.get("sensor_status", {}) if connected else {}
    return {
        "connected": connected,
        "last_seen": last_hardware_telemetry.get("timestamp"),
        "sensors": {name: bool(sensors.get(name, False)) for name in ("temperature", "oil_level", "voltage", "current")}
    }

@app.post("/api/runtime/mode")
def set_runtime_mode(data: RuntimeModeInput):
    """Switch between the review simulator and the live ESP32 stream."""
    mode = data.mode.upper()
    if mode not in {"DEMO", "REAL"}:
        raise HTTPException(status_code=400, detail="Mode must be DEMO or REAL.")
    if mode == "REAL":
        sim_controller.stop()
    else:
        sim_controller.start()
    return {"mode": mode, "simulation_running": sim_controller.is_running}

@app.get("/api/telemetry/latest")
def get_latest(transformer_id: str = "TR-001"):
    latest = get_latest_telemetry(transformer_id)
    if not latest:
        raise HTTPException(status_code=404, detail="No telemetry records found.")
    
    ml_res = predictor.predict(
        temperature=latest["temperature"],
        oil_level=latest["oil_level"],
        voltage=latest["voltage"],
        current=latest["current"]
    )
    latest["risk_factors"] = ml_res["risk_factors"]
    latest["recommendations"] = ml_res["recommendations"]
    return latest

@app.get("/api/telemetry/history")
def get_history(transformer_id: str = "TR-001", limit: int = 50):
    return get_telemetry_history(transformer_id, limit=limit)

@app.get("/api/alerts")
def get_alerts(transformer_id: str = "TR-001", limit: int = 30):
    return get_recent_alerts(transformer_id, limit=limit)

@app.post("/api/alerts/clear")
def clear_all_alerts(transformer_id: str = "TR-001"):
    clear_alerts(transformer_id)
    return {"status": "success", "message": "All alerts cleared."}

@app.get("/api/assets")
def get_assets():
    """Returns fleet of distribution transformers."""
    return get_transformers()

@app.get("/api/maintenance")
def get_maintenance(transformer_id: str = "TR-001"):
    """Returns maintenance logs and inspection history."""
    return get_maintenance_records(transformer_id)

@app.post("/api/maintenance")
def create_maintenance(data: MaintenanceInput):
    """Logs a new maintenance activity."""
    rec_id = add_maintenance_record(
        transformer_id=data.transformer_id,
        activity_type=data.activity_type,
        technician=data.technician,
        parameter_impacted=data.parameter_impacted,
        findings=data.findings
    )
    return {"status": "success", "id": rec_id, "message": "Maintenance record created."}

@app.delete("/api/maintenance/{record_id}")
def delete_maintenance(record_id: int):
    """Deletes an individual maintenance log entry by ID."""
    success = delete_maintenance_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Maintenance record not found.")
    return {"status": "success", "message": f"Maintenance record {record_id} deleted."}

@app.delete("/api/maintenance")
def delete_maintenance_by_param(id: Optional[int] = Query(None)):
    """Deletes an individual maintenance log entry via query parameter."""
    if id is None:
        raise HTTPException(status_code=400, detail="Missing record id parameter.")
    success = delete_maintenance_record(id)
    if not success:
        raise HTTPException(status_code=404, detail="Maintenance record not found.")
    return {"status": "success", "message": f"Maintenance record {id} deleted."}

@app.get("/api/analytics/summary")
def get_analytics(transformer_id: str = "TR-001"):
    """Returns aggregate sensor statistics and health distribution for analytics."""
    return get_analytics_summary(transformer_id)

@app.get("/api/reports/export-csv")
def export_csv(transformer_id: str = "TR-001", limit: int = 200):
    """Exports historical telemetry records as a downloadable CSV file."""
    records = get_telemetry_history(transformer_id, limit=limit)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Record_ID", "Transformer_ID", "Timestamp",
        "Temperature_C", "Oil_Level_Pct", "Voltage_V", "Current_A",
        "Health_Status", "AI_Confidence_Pct"
    ])
    for r in records:
        writer.writerow([
            r["id"], r["transformer_id"], r["timestamp"],
            r["temperature"], r["oil_level"], r["voltage"], r["current"],
            r["health_status"], r["confidence"]
        ])
    
    filename = f"PowerSense_{transformer_id}_Telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/model/info")
def get_model_info():
    """Returns trained Random Forest model hyperparameters, accuracy, and feature importances."""
    return predictor.get_metadata()

# Simulation & Demonstration Controls (For Review Demo)

@app.post("/api/simulation/inject-scenario")
async def inject_scenario(data: ScenarioInput):
    """
    Sets the simulator preset scenario and immediately transmits a test sample.
    Scenarios: 'NORMAL', 'WARNING_THERMAL', 'CRITICAL_LEAK', 'CRITICAL_OVERLOAD'
    """
    ok = sim_controller.simulator.set_scenario(data.scenario, immediate=True)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid scenario name.")
    
    sample = sim_controller.simulator.next_sample()
    record = await process_and_broadcast_telemetry(sample, source=f"Demo Scenario: {data.scenario}")
    return {"status": "success", "record": record}

@app.post("/api/simulation/toggle")
def toggle_simulation():
    sim_controller.is_running = not sim_controller.is_running
    return {"is_running": sim_controller.is_running}

@app.get("/api/simulation/status")
def simulation_status():
    return {
        "is_running": sim_controller.is_running,
        "mode": sim_controller.simulator.mode,
        "interval_seconds": sim_controller.interval
    }

# WebSockets Endpoint
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        latest = get_latest_telemetry("TR-001")
        if latest:
            ml_res = predictor.predict(
                temperature=latest["temperature"],
                oil_level=latest["oil_level"],
                voltage=latest["voltage"],
                current=latest["current"]
            )
            latest["risk_factors"] = ml_res["risk_factors"]
            latest["recommendations"] = ml_res["recommendations"]
            latest["alerts"] = ml_res["alerts"]
            await websocket.send_json({"type": "INITIAL_STATE", "data": latest})

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# Serve Web Dashboard
@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "Frontend static/index.html initializing..."})

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n=======================================================")
    print("  PowerSense - Smart Transformer Health Monitoring System  ")
    print("  FastAPI Server Running at: http://127.0.0.1:8000     ")
    print("  Web Dashboard:             http://127.0.0.1:8000/    ")
    print("  API Docs (Swagger):        http://127.0.0.1:8000/docs")
    print("=======================================================\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
