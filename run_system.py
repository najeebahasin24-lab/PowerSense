"""
AI-Based Smart Transformer Health Monitoring System
One-Click Launch Script
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_file = os.path.join(base_dir, "ml_model", "transformer_rf_model.joblib")

    print("=======================================================================")
    print("   AI-BASED SMART TRANSFORMER HEALTH MONITORING SYSTEM               ")
    print("   Department of Computer Science & Engineering                     ")
    print("=======================================================================")

    # 1. Check ML Model
    if not os.path.exists(model_file):
        print("\n[ML] Trained Random Forest model not found. Training model now...")
        train_script = os.path.join(base_dir, "ml_model", "train_model.py")
        subprocess.run([sys.executable, train_script], check=True)
    else:
        print("\n[ML] Pre-trained Random Forest model found.")

    # 2. Database check
    from database.db import init_db
    init_db()
    print("[DB] SQLite telemetry database initialized.")

    # 3. Launch FastAPI Server
    print("\n[SERVER] Launching FastAPI Backend & Real-Time Dashboard...")
    print("  -> Dashboard URL:    http://127.0.0.1:8000/")
    print("  -> API Docs Swagger: http://127.0.0.1:8000/docs")
    print("  -> ESP32 Ingestion:  POST http://127.0.0.1:8000/api/telemetry")
    print("\nPress Ctrl+C to terminate.")
    print("=======================================================================\n")

    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
