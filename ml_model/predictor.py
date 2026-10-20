"""
Transformer Health Predictor Service
Wraps the trained Random Forest Classifier for real-time inference.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "transformer_rf_model.joblib")
METADATA_FILE = os.path.join(MODEL_DIR, "model_metadata.json")

class TransformerHealthPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(f"Model file not found at {MODEL_FILE}. Run train_model.py first.")
        
        self.model = joblib.load(MODEL_FILE)
        self.metadata = {}
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r") as f:
                self.metadata = json.load(f)
        
        self.class_names = ["NORMAL", "WARNING", "CRITICAL"]
        self.feature_cols = ["temperature", "oil_level", "voltage", "current", "apparent_power", "thermal_stress_index"]

    def predict(self, temperature: float, oil_level: float, voltage: float, current: float):
        """
        Runs ML inference on sensor readings and returns health status, confidence,
        probabilities, diagnostic flags, and engineering recommendations.
        """
        temperature = float(temperature)
        oil_level = float(oil_level)
        voltage = float(voltage)
        current = float(current)

        # Feature engineering
        apparent_power = round(voltage * current, 2)
        thermal_stress_index = round(temperature / (oil_level + 1e-3), 3)

        df_input = pd.DataFrame([{
            "temperature": temperature,
            "oil_level": oil_level,
            "voltage": voltage,
            "current": current,
            "apparent_power": apparent_power,
            "thermal_stress_index": thermal_stress_index
        }])[self.feature_cols]

        pred_idx = int(self.model.predict(df_input)[0])
        status = self.class_names[pred_idx]

        # Probability distribution across classes
        probs = self.model.predict_proba(df_input)[0]
        prob_dict = {
            self.class_names[i]: round(float(probs[i]), 4) for i in range(len(self.class_names))
        }
        confidence = round(float(probs[pred_idx]) * 100, 1)

        # Expert diagnostic analysis & alert conditions
        risk_factors = []
        recommendations = []
        alerts = []

        if temperature >= 85.0:
            risk_factors.append(f"Core/TEMPERATURE ({temperature:.1f}°C) exceeds critical safety limit (85°C).")
            alerts.append({"severity": "CRITICAL", "param": "Temperature", "msg": f"Extreme thermal runaway hazard: {temperature:.1f}°C"})
            recommendations.append("Immediate emergency shutdown / load disconnection to prevent winding fire.")
        elif temperature >= 65.0:
            risk_factors.append(f"Elevated operating temperature ({temperature:.1f}°C).")
            alerts.append({"severity": "WARNING", "param": "Temperature", "msg": f"High temperature warning: {temperature:.1f}°C"})
            recommendations.append("Activate secondary cooling fans and inspect thermal dissipation radiators.")

        if oil_level < 45.0:
            risk_factors.append(f"Dielectric oil level ({oil_level:.1f}%) dangerously depleted.")
            alerts.append({"severity": "CRITICAL", "param": "Oil Level", "msg": f"Critical low oil level: {oil_level:.1f}%"})
            recommendations.append("Top up dielectric insulating oil immediately to avoid internal arcing.")
        elif oil_level < 70.0:
            risk_factors.append(f"Oil level below nominal margin ({oil_level:.1f}%).")
            alerts.append({"severity": "WARNING", "param": "Oil Level", "msg": f"Oil reservoir low: {oil_level:.1f}%"})
            recommendations.append("Inspect oil tank seals for seepage or micro-leaks.")

        if current > 6.5:
            risk_factors.append(f"Severe overcurrent drawn ({current:.2f}A) - potential short circuit or major overload.")
            alerts.append({"severity": "CRITICAL", "param": "Current", "msg": f"Overcurrent surge: {current:.2f}A"})
            recommendations.append("Trip secondary circuit breaker and inspect downstream loads.")
        elif current > 4.5:
            risk_factors.append(f"Operating above rated load current ({current:.2f}A).")
            alerts.append({"severity": "WARNING", "param": "Current", "msg": f"Load current elevated: {current:.2f}A"})
            recommendations.append("Distribute load across backup transformer phases.")

        if voltage < 190.0:
            risk_factors.append(f"Severe undervoltage sag ({voltage:.1f}V).")
            alerts.append({"severity": "CRITICAL", "param": "Voltage", "msg": f"Severe voltage sag: {voltage:.1f}V"})
            recommendations.append("Inspect grid feeder line and tap-changer settings.")
        elif voltage > 255.0:
            risk_factors.append(f"Dangerous overvoltage surge ({voltage:.1f}V).")
            alerts.append({"severity": "CRITICAL", "param": "Voltage", "msg": f"Overvoltage surge: {voltage:.1f}V"})
            recommendations.append("Engage surge arresters and check primary bus regulator.")
        elif voltage < 215.0 or voltage > 240.0:
            risk_factors.append(f"Voltage variation out of nominal tolerance ({voltage:.1f}V).")
            alerts.append({"severity": "WARNING", "param": "Voltage", "msg": f"Voltage fluctuation: {voltage:.1f}V"})

        if not risk_factors:
            risk_factors.append("All physical parameters within optimal IEEE standard margins.")
            recommendations.append("Transformer operating efficiently. Routine maintenance scheduled.")

        return {
            "status": status,
            "confidence": confidence,
            "probabilities": prob_dict,
            "apparent_power": apparent_power,
            "thermal_stress_index": thermal_stress_index,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "alerts": alerts
        }

    def get_metadata(self):
        return self.metadata

# Singleton instance
predictor = TransformerHealthPredictor()
