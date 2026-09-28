"""
SQLite Database Layer for Transformer Health Telemetry & Alerts
PowerSense Industrial Condition Monitoring System
"""

import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "transformer_health.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Transformers fleet metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transformers (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        rated_kva REAL DEFAULT 1.0,
        rated_voltage REAL DEFAULT 230.0,
        cooling_type TEXT DEFAULT 'ONAN',
        installation_date TEXT DEFAULT '2025-01-15',
        status TEXT DEFAULT 'OPERATIONAL',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ensure missing columns exist in existing transformers table
    cursor.execute("PRAGMA table_info(transformers)")
    columns = [col[1] for col in cursor.fetchall()]
    if "cooling_type" not in columns:
        cursor.execute("ALTER TABLE transformers ADD COLUMN cooling_type TEXT DEFAULT 'ONAN'")
    if "installation_date" not in columns:
        cursor.execute("ALTER TABLE transformers ADD COLUMN installation_date TEXT DEFAULT '2025-01-15'")
    if "status" not in columns:
        cursor.execute("ALTER TABLE transformers ADD COLUMN status TEXT DEFAULT 'OPERATIONAL'")

    # Telemetry time-series table (Focusing strictly on the 4 sensors)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transformer_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        temperature REAL NOT NULL,
        oil_level REAL NOT NULL,
        voltage REAL NOT NULL,
        current REAL NOT NULL,
        apparent_power REAL NOT NULL,
        thermal_stress_index REAL NOT NULL,
        health_status TEXT NOT NULL,
        confidence REAL NOT NULL,
        probabilities_json TEXT NOT NULL,
        alert_flag INTEGER DEFAULT 0,
        FOREIGN KEY (transformer_id) REFERENCES transformers(id)
    )
    """)

    # Alerts history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transformer_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        severity TEXT NOT NULL,
        parameter TEXT NOT NULL,
        value REAL NOT NULL,
        message TEXT NOT NULL,
        resolved INTEGER DEFAULT 0,
        FOREIGN KEY (transformer_id) REFERENCES transformers(id)
    )
    """)

    # Maintenance work orders & inspection history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transformer_id TEXT NOT NULL,
        date TEXT NOT NULL,
        activity_type TEXT NOT NULL,
        technician TEXT NOT NULL,
        parameter_impacted TEXT NOT NULL,
        findings TEXT NOT NULL,
        status TEXT DEFAULT 'Completed',
        FOREIGN KEY (transformer_id) REFERENCES transformers(id)
    )
    """)

    # Seed Fleet Transformers
    fleet = [
        ('TR-001', 'Transformer 001 - Smart Substation Feeder 01', 'Substation Bay A (Lab Unit 1)', 1.0, 230.0, 'ONAN', '2025-01-15', 'OPERATIONAL'),
        ('TR-002', 'Transformer 002 - Industrial Auxiliary Feeder', 'Substation Bay B', 1.0, 230.0, 'ONAN', '2024-11-20', 'STANDBY'),
        ('TR-003', 'Transformer 003 - Grid Inter-Tie Testbed', 'High Voltage Lab Bay C', 1.0, 230.0, 'ONAN', '2025-03-01', 'MAINTENANCE')
    ]
    for unit in fleet:
        cursor.execute("""
        INSERT OR REPLACE INTO transformers (id, name, location, rated_kva, rated_voltage, cooling_type, installation_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, unit)

    # Seed Initial Maintenance History for TR-001
    cursor.execute("SELECT COUNT(*) as cnt FROM maintenance WHERE transformer_id = 'TR-001'")
    if cursor.fetchone()["cnt"] == 0:
        initial_logs = [
            ('TR-001', '2026-08-12', 'Oil Level Replenishment', 'Eng. R. Sharma', 'Oil Level', 'Topped up 1.5L mineral dielectric oil; resealed conservator valve.', 'Completed'),
            ('TR-001', '2026-06-04', 'ACS712 Current Sensor Calibration', 'Saumya Kumari', 'Current', 'Recalibrated zero-offset ADC voltage to 1.65V rail; tested with resistive load.', 'Completed'),
            ('TR-001', '2026-03-18', 'Thermal Core Sensor Verification', 'S Najeeba Hasin', 'Temperature', 'Calibrated LM35 probe against high-precision infrared pyrometer within ±0.2°C.', 'Completed'),
            ('TR-001', '2025-12-10', 'Dielectric Breakdown Voltage (BDV) Test', 'Shanmuga Priya M.E.', 'Oil Level', 'Oil BDV measured at 48 kV; dielectric insulation compliant with IEEE C57.104.', 'Completed')
        ]
        for log in initial_logs:
            cursor.execute("""
            INSERT INTO maintenance (transformer_id, date, activity_type, technician, parameter_impacted, findings, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, log)

    conn.commit()
    conn.close()

def save_telemetry(data: dict):
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_flag = 1 if (data.get("alerts") and len(data["alerts"]) > 0) else 0

    cursor.execute("""
    INSERT INTO telemetry (
        transformer_id, timestamp, temperature, oil_level, voltage, current,
        apparent_power, thermal_stress_index, health_status, confidence,
        probabilities_json, alert_flag
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("transformer_id", "TR-001"),
        timestamp,
        float(data["temperature"]),
        float(data["oil_level"]),
        float(data["voltage"]),
        float(data["current"]),
        float(data.get("apparent_power", data["voltage"] * data["current"])),
        float(data.get("thermal_stress_index", 0.0)),
        data["health_status"],
        float(data.get("confidence", 95.0)),
        json.dumps(data.get("probabilities", {})),
        alert_flag
    ))
    telemetry_id = cursor.lastrowid

    # Insert any associated alerts
    if data.get("alerts"):
        for alt in data["alerts"]:
            cursor.execute("""
            INSERT INTO alerts (transformer_id, timestamp, severity, parameter, value, message)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data.get("transformer_id", "TR-001"),
                timestamp,
                alt.get("severity", "WARNING"),
                alt.get("param", "General"),
                float(data.get(alt.get("param", "").lower(), 0.0)) if alt.get("param", "").lower() in data else 0.0,
                alt.get("msg", "Abnormal telemetry detected.")
            ))

    conn.commit()
    conn.close()
    return telemetry_id

def get_latest_telemetry(transformer_id="TR-001"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM telemetry 
    WHERE transformer_id = ? 
    ORDER BY id DESC LIMIT 1
    """, (transformer_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["probabilities"] = json.loads(d["probabilities_json"])
        return d
    return None

def get_telemetry_history(transformer_id="TR-001", limit=40):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM (
        SELECT * FROM telemetry 
        WHERE transformer_id = ? 
        ORDER BY id DESC LIMIT ?
    ) ORDER BY id ASC
    """, (transformer_id, limit))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["probabilities"] = json.loads(d["probabilities_json"])
        result.append(d)
    return result

def get_recent_alerts(transformer_id="TR-001", limit=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM alerts 
    WHERE transformer_id = ? 
    ORDER BY id DESC LIMIT ?
    """, (transformer_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_alerts(transformer_id="TR-001"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alerts WHERE transformer_id = ?", (transformer_id,))
    conn.commit()
    conn.close()
    return True

def get_transformers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transformers ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_maintenance_records(transformer_id="TR-001"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM maintenance 
    WHERE transformer_id = ? 
    ORDER BY id DESC
    """, (transformer_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_maintenance_record(transformer_id: str, activity_type: str, technician: str, parameter_impacted: str, findings: str):
    conn = get_connection()
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO maintenance (transformer_id, date, activity_type, technician, parameter_impacted, findings, status)
    VALUES (?, ?, ?, ?, ?, ?, 'Completed')
    """, (transformer_id, date_str, activity_type, technician, parameter_impacted, findings))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_analytics_summary(transformer_id="TR-001"):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Aggregated stats for the 4 sensors
    cursor.execute("""
    SELECT 
        COUNT(*) as total_samples,
        MIN(temperature) as min_temp, MAX(temperature) as max_temp, AVG(temperature) as avg_temp,
        MIN(oil_level) as min_oil, MAX(oil_level) as max_oil, AVG(oil_level) as avg_oil,
        MIN(voltage) as min_volt, MAX(voltage) as max_volt, AVG(voltage) as avg_volt,
        MIN(current) as min_curr, MAX(current) as max_curr, AVG(current) as avg_curr
    FROM telemetry WHERE transformer_id = ?
    """, (transformer_id,))
    stats = dict(cursor.fetchone() or {})

    # Status distribution
    cursor.execute("""
    SELECT health_status, COUNT(*) as count 
    FROM telemetry WHERE transformer_id = ? 
    GROUP BY health_status
    """, (transformer_id,))
    dist = {r["health_status"]: r["count"] for r in cursor.fetchall()}
    stats["distribution"] = dist

    # Total alerts
    cursor.execute("SELECT COUNT(*) as total_alerts FROM alerts WHERE transformer_id = ?", (transformer_id,))
    stats["total_alerts"] = cursor.fetchone()["total_alerts"]

    conn.close()
    return stats

# Initialize on import
init_db()
