"""
Transformer Sensor Telemetry Simulator
Mimics real-time ESP32 hardware transmissions.
Can be invoked as a standalone script or imported as an async background task.
"""

import time
import random
import math
import requests
import json
from datetime import datetime

class SensorSimulator:
    def __init__(self, target_url="http://127.0.0.1:8000/api/telemetry"):
        self.target_url = target_url
        self.transformer_id = "TR-001"
        self.running = False
        self.mode = "NORMAL"  # "NORMAL", "WARNING_THERMAL", "CRITICAL_LEAK", "CRITICAL_OVERLOAD"
        
        # State variables for smooth physical simulation
        self.temp = 45.0
        self.oil = 92.0
        self.voltage = 230.0
        self.current = 2.8
        self.time_step = 0

    def set_scenario(self, scenario_name: str, immediate: bool = True):
        valid = ["NORMAL", "WARNING_THERMAL", "CRITICAL_LEAK", "CRITICAL_OVERLOAD"]
        if scenario_name.upper() in valid:
            self.mode = scenario_name.upper()
            if immediate:
                if self.mode == "NORMAL":
                    self.temp, self.oil, self.voltage, self.current = 45.2, 91.5, 230.1, 2.75
                elif self.mode == "WARNING_THERMAL":
                    self.temp, self.oil, self.voltage, self.current = 76.5, 78.0, 224.5, 5.35
                elif self.mode == "CRITICAL_LEAK":
                    self.temp, self.oil, self.voltage, self.current = 91.2, 33.5, 221.0, 5.95
                elif self.mode == "CRITICAL_OVERLOAD":
                    self.temp, self.oil, self.voltage, self.current = 68.4, 85.0, 194.2, 8.65
            return True
        return False

    def next_sample(self):
        """Generates realistic continuous time-series physics with minor Gaussian noise."""
        self.time_step += 1
        noise = lambda scale: random.gauss(0, scale)

        if self.mode == "NORMAL":
            target_temp = 46.0 + 3.0 * math.sin(self.time_step * 0.1)
            target_oil = 90.0 - (self.time_step * 0.01) % 5.0
            target_volt = 230.0 + 2.0 * math.sin(self.time_step * 0.15)
            target_curr = 2.8 + 0.6 * math.sin(self.time_step * 0.08)

        elif self.mode == "WARNING_THERMAL":
            target_temp = 75.0 + 4.0 * math.sin(self.time_step * 0.1)
            target_oil = 76.0
            target_volt = 225.0 + 3.0 * math.sin(self.time_step * 0.1)
            target_curr = 5.2 + 0.5 * math.sin(self.time_step * 0.12)

        elif self.mode == "CRITICAL_LEAK":
            target_temp = 90.0 + 3.0 * math.sin(self.time_step * 0.1)
            target_oil = 34.0 - (self.time_step * 0.1) % 8.0
            target_volt = 221.0
            target_curr = 5.9 + 0.4 * math.sin(self.time_step * 0.1)

        elif self.mode == "CRITICAL_OVERLOAD":
            target_temp = 66.0 + (self.time_step * 0.5) % 15.0
            target_oil = 85.0
            target_volt = 195.0 + noise(2.0)
            target_curr = 8.6 + noise(0.4)

        else:
            target_temp, target_oil, target_volt, target_curr = 45.0, 90.0, 230.0, 2.8

        # Smooth physical transition towards target
        self.temp += (target_temp - self.temp) * 0.35 + noise(0.2)
        self.oil += (target_oil - self.oil) * 0.25 + noise(0.1)
        self.voltage += (target_volt - self.voltage) * 0.5 + noise(0.4)
        self.current += (target_curr - self.current) * 0.4 + noise(0.08)

        # Clamping
        self.temp = max(15.0, min(125.0, self.temp))
        self.oil = max(5.0, min(100.0, self.oil))
        self.voltage = max(120.0, min(290.0, self.voltage))
        self.current = max(0.1, min(15.0, self.current))

        payload = {
            "transformer_id": self.transformer_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(self.temp, 2),
            "oil_level": round(self.oil, 2),
            "voltage": round(self.voltage, 2),
            "current": round(self.current, 2)
        }
        return payload

    def send_telemetry(self, payload=None):
        if payload is None:
            payload = self.next_sample()
        try:
            resp = requests.post(self.target_url, json=payload, timeout=2.0)
            return resp.status_code == 200, resp.json() if resp.status_code == 200 else resp.text
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/api/telemetry"
    print(f"Starting Standalone Sensor Simulator streaming to {url}...")
    sim = SensorSimulator(target_url=url)
    try:
        while True:
            data = sim.next_sample()
            ok, resp = sim.send_telemetry(data)
            status = resp.get('health_status', 'N/A') if isinstance(resp, dict) else 'ERR'
            print(f"[{data['timestamp']}] T={data['temperature']}°C | Oil={data['oil_level']}% | V={data['voltage']}V | I={data['current']}A => Status: {status}")
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
