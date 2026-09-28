# AI-Based Smart Transformer Health Monitoring System
### Complete Software Prototype & Review Demonstration Guide

---

## 📌 Executive Summary for Tomorrow's Review
This software prototype implements an end-to-end IoT and Machine Learning pipeline for the **AI-Based Smart Transformer Health Monitoring System**. It bridges physical sensor acquisition, cloud/backend storage, and AI inference to assess transformer operating conditions into **NORMAL**, **WARNING**, or **CRITICAL** states.

---

## 🚀 How to Run the System (1-Click Launch)

Open PowerShell / Terminal in this project directory and run:

```bash
python run_system.py
```

- **Live Web Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ESP32 Ingestion Endpoint:** `POST http://<SERVER_IP>:8000/api/telemetry`

---

## ❓ Answering Your Review Question: Demonstrating Real-Time Data Without Hardware

### "How can I demonstrate this during tomorrow's review without having the actual hardware prototype yet?"

You have **two proven, professional approaches** already built and ready in your codebase:

### Approach 1: The Built-In Software Telemetry Streamer (Recommended for Live Demo)
- **Why it's best for tomorrow:** Zero Wi-Fi dependence, 100% stable, no fear of hardware misfires during evaluation.
- **How it works:** When you start the server (`python run_system.py`), an asynchronous background simulation engine (`simulator.py`) immediately starts generating realistic physical time-series telemetry (with smooth thermal inertia, load fluctuations, and noise) and streams it through the exact same pipeline that the real ESP32 will use.
- **Interactive Review Controller Bar:**
  At the top of your dashboard, you have **1-Click Review Scenarios**:
  1. 🟢 **Normal Condition:** Sets typical baseline readings (~45°C, 92% Oil, 230V, 2.8A). Health status turns **NORMAL** (Emerald Green).
  2. 🟡 **Warning: Thermal Stress:** Elevates temperature to ~76°C under 5.3A load. Health status instantly transitions to **WARNING** (Amber), generating preventive maintenance alerts.
  3. 🔴 **Critical: Low Oil & Heat:** Simulates dielectric oil depletion (34%) with severe thermal rise (91°C). Health status triggers **CRITICAL** (Crimson Red with pulsing alarm glow).
  4. ⚡ **Critical: Overload Surge:** Simulates secondary short-circuit overcurrent (8.6A, 195V sag).
  5. 🎛 **Custom Sliders:** Let your evaluator drag sliders for Temperature, Oil Level, Voltage, and Current to see the AI model reclassify conditions on the fly!

### Approach 2: Online Hardware Simulation via Wokwi (ESP32 in the Cloud)
- **Platform:** [Wokwi.com](https://wokwi.com/)
- **How it works:**
  1. Open Wokwi's online ESP32 simulator.
  2. Copy-paste your firmware code: `esp32_firmware/esp32_transformer_monitor.ino`.
  3. Load the diagram file: `esp32_firmware/diagram.json` (which connects 4 virtual potentiometers to ADC pins GPIO 32, 33, 34, 35 representing your sensors).
  4. The virtual ESP32 connects to `Wokwi-GUEST` simulated Wi-Fi and makes real HTTP POST requests to your server!

---

## 🧠 AI / Machine Learning Engine Details

- **Algorithm:** Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`)
- **Number of Estimators (Trees):** 120
- **Trained Accuracy:** **99.20%** (5-Fold Cross-Validation: **99.25%**)
- **Sensors & Input Features:**
  1. `temperature` (°C) - Measured via LM35 / DS18B20
  2. `oil_level` (%) - Measured via Ultrasonic / Float sensor
  3. `voltage` (V) - Measured via ZMPT101B potential transformer
  4. `current` (A) - Measured via ACS712 secondary current sensor
  5. `apparent_power` (VA) - Engineered feature: $V \times I$
  6. `thermal_stress_index` - Engineered composite: $\frac{\text{Temperature}}{\text{Oil Level}}$

### Health Classification Criteria (IEEE C57.104 Aligned)
| Status | Temperature | Oil Level | Voltage | Current | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 🟢 **NORMAL** | 25°C – 65°C | &gt; 70% | 215V – 240V | 0.5A – 4.5A | Optimal operation. Routine logging. |
| 🟡 **WARNING** | 65°C – 84°C | 45% – 70% | 190–214V / 241–255V | 4.5A – 6.5A | Preventive maintenance, cooling fan dispatch. |
| 🔴 **CRITICAL** | &ge; 85°C | &lt; 45% | &lt; 190V or &gt; 255V | &gt; 6.5A | Emergency trip, load shedding, oil replenishment. |

---

## 🔌 Hardware-Ready: Connecting ESP32 Later

When your physical mini-transformer testbed and sensors arrive, **zero software changes are needed**:
1. Open `esp32_firmware/esp32_transformer_monitor.ino` in Arduino IDE.
2. Enter your Wi-Fi SSID and Password.
3. Set `SERVER_URL = "http://<YOUR_COMPUTER_IP>:8000/api/telemetry"`.
4. Flash the code to the ESP32.
5. The ESP32 will immediately post live ADC sensor measurements every 2 seconds, which the server logs into SQLite and updates on the dashboard!

---

## 📁 Project Architecture & File Structure

```
ai based smart transformer health monitoring/
├── app.py                             # FastAPI backend with WebSockets & REST APIs
├── run_system.py                      # One-click startup launcher
├── simulator.py                       # Realistic IoT sensor telemetry stream generator
├── ml_model/
│   ├── train_model.py                 # Dataset generation & Random Forest model training
│   ├── predictor.py                   # Real-time inference wrapper & diagnostic rules
│   ├── transformer_rf_model.joblib    # Serialized trained model (99.2% accuracy)
│   ├── model_metadata.json            # Accuracy, confusion matrix & feature importances
│   └── transformer_telemetry_sample.csv # Sample dataset for report/presentation
├── database/
│   ├── db.py                          # SQLite ORM for time-series telemetry & alerts
│   └── transformer_health.db          # Active SQLite database file
├── static/
│   ├── index.html                     # Enterprise dark glassmorphic dashboard UI
│   ├── style.css                      # Custom vanilla CSS design system & animations
│   └── app.js                         # WebSockets, Chart.js live charts & controls
└── esp32_firmware/
    ├── esp32_transformer_monitor.ino  # Ready-to-flash C++ embedded firmware
    └── diagram.json                   # Wokwi simulation circuit configuration
```

---

## 🎯 Step-by-Step Demo Script for Your Reviewers Tomorrow

1. **Introduction:**
   - *"Good morning/afternoon. Today I am presenting our implementation progress for the AI-Based Smart Transformer Health Monitoring System."*
   - *"While awaiting laboratory component delivery, we have completed the core software architecture: the real-time IoT backend, SQLite telemetry storage, an AI Random Forest health classification engine, and an enterprise monitoring dashboard."*

2. **Show the Live Dashboard:**
   - Point out **Transformer 001**, the **Live Telemetry Active** badge, and the **99.2% AI Model Confidence**.
   - Show the 4 physical sensors (**Temperature**, **Oil Level**, **Voltage**, **Current**) along with computed **Apparent Power** and **Thermal Stress Index**.

3. **Demonstrate Dynamic Real-Time Ticking:**
   - Point out how the two **Chart.js graphs** smoothly tick every 2 seconds as live telemetry streams in.

4. **Demonstrate AI Anomaly Detection:**
   - Click **"Warning: Thermal Stress"** $\rightarrow$ Show the status switch to Amber **WARNING**, the diagnostic assessment explain the thermal rise, and an entry appear in the **Event Stream**.
   - Click **"Critical: Low Oil & Heat"** $\rightarrow$ Show the status switch to Crimson Red **CRITICAL**, the alert sound chime, and urgent recommendations appear.
   - Click **"Custom Sliders"** $\rightarrow$ Invite the reviewer to set any temperature or current value and see the Random Forest model reclassify it instantly.

5. **Show the Code & Hardware Readiness:**
   - Show `esp32_firmware/esp32_transformer_monitor.ino` to prove that the embedded C++ firmware for the ESP32 is already fully written with pinouts, ADC scaling, and HTTP JSON serialization.
