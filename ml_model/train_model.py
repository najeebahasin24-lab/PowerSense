"""
AI-Based Smart Transformer Health Monitoring System
Machine Learning Model Training Script
Algorithm: Random Forest Classifier (Multi-class: NORMAL, WARNING, CRITICAL)

Features:
  - temperature (°C)
  - oil_level (%)
  - voltage (V)
  - current (A)
  - apparent_power (VA)
  - thermal_stress_index
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "transformer_rf_model.joblib")
METADATA_FILE = os.path.join(MODEL_DIR, "model_metadata.json")

def generate_transformer_dataset(n_samples=6000, random_state=42):
    """
    Generates realistic transformer telemetry based on electrical engineering
    and IEEE C57.104 transformer health guidelines.
    """
    np.random.seed(random_state)
    
    # Class 0: NORMAL (approx 50% of operating history)
    n_normal = int(n_samples * 0.50)
    temp_norm = np.random.normal(loc=46.0, scale=8.0, size=n_normal).clip(25.0, 64.9)
    oil_norm = np.random.normal(loc=88.0, scale=6.0, size=n_normal).clip(72.0, 100.0)
    volt_norm = np.random.normal(loc=230.0, scale=3.5, size=n_normal).clip(216.0, 239.5)
    curr_norm = np.random.normal(loc=2.6, scale=0.8, size=n_normal).clip(0.6, 4.4)
    labels_norm = np.zeros(n_normal, dtype=int)
    
    # Class 1: WARNING (approx 28% of operating history)
    # Causes: Elevated load, mild oil depletion, voltage fluctuations, warm ambient
    n_warning = int(n_samples * 0.28)
    
    # Mix of warning scenarios:
    # 1. Thermal stress (65 - 84°C)
    # 2. Moderate oil loss (48 - 71%)
    # 3. Voltage sag/swell (195-215V or 240-252V)
    # 4. Overcurrent (4.5 - 6.4A)
    scenario = np.random.choice([0, 1, 2, 3], size=n_warning, p=[0.35, 0.25, 0.20, 0.20])
    
    temp_warn = np.random.normal(loc=55.0, scale=7.0, size=n_warning)
    oil_warn = np.random.normal(loc=78.0, scale=8.0, size=n_warning)
    volt_warn = np.random.normal(loc=230.0, scale=4.0, size=n_warning)
    curr_warn = np.random.normal(loc=3.2, scale=0.9, size=n_warning)
    
    for i in range(n_warning):
        if scenario[i] == 0:  # Thermal stress
            temp_warn[i] = np.random.uniform(65.0, 84.0)
            curr_warn[i] = np.random.uniform(3.5, 5.8)
        elif scenario[i] == 1:  # Low oil
            oil_warn[i] = np.random.uniform(48.0, 71.0)
            temp_warn[i] = np.random.uniform(55.0, 78.0)
        elif scenario[i] == 2:  # Voltage irregularity
            volt_warn[i] = np.random.choice([np.random.uniform(195.0, 214.0), np.random.uniform(241.0, 252.0)])
        elif scenario[i] == 3:  # Moderate Overload
            curr_warn[i] = np.random.uniform(4.5, 6.4)
            temp_warn[i] = np.random.uniform(58.0, 80.0)
            
    temp_warn = temp_warn.clip(25.0, 84.9)
    oil_warn = oil_warn.clip(45.0, 100.0)
    volt_warn = volt_warn.clip(192.0, 254.0)
    curr_warn = curr_warn.clip(0.6, 6.4)
    labels_warn = np.ones(n_warning, dtype=int)
    
    # Class 2: CRITICAL (approx 22% of operating history)
    # Causes: Severe overheating (>85°C), low oil level (<48%), severe overcurrent/short circuit (>6.5A), severe brownout/overvoltage (<190V or >255V)
    n_critical = n_samples - n_normal - n_warning
    crit_scenario = np.random.choice([0, 1, 2, 3, 4], size=n_critical, p=[0.25, 0.25, 0.20, 0.15, 0.15])
    
    temp_crit = np.random.normal(loc=65.0, scale=10.0, size=n_critical)
    oil_crit = np.random.normal(loc=60.0, scale=15.0, size=n_critical)
    volt_crit = np.random.normal(loc=225.0, scale=12.0, size=n_critical)
    curr_crit = np.random.normal(loc=4.5, scale=2.0, size=n_critical)
    
    for i in range(n_critical):
        if crit_scenario[i] == 0:  # Dangerous thermal runaway
            temp_crit[i] = np.random.uniform(85.0, 115.0)
        elif crit_scenario[i] == 1:  # Severe oil depletion (insulation risk)
            oil_crit[i] = np.random.uniform(15.0, 46.0)
            temp_crit[i] = np.random.uniform(70.0, 95.0)
        elif crit_scenario[i] == 2:  # Short circuit / Massive overcurrent
            curr_crit[i] = np.random.uniform(6.6, 12.0)
            temp_crit[i] = np.random.uniform(75.0, 105.0)
            volt_crit[i] = np.random.uniform(170.0, 215.0)
        elif crit_scenario[i] == 3:  # Severe voltage fault (surge or deep sag)
            volt_crit[i] = np.random.choice([np.random.uniform(140.0, 189.0), np.random.uniform(256.0, 280.0)])
        elif crit_scenario[i] == 4:  # Compound failure: High temp + low oil
            temp_crit[i] = np.random.uniform(82.0, 110.0)
            oil_crit[i] = np.random.uniform(20.0, 45.0)
            curr_crit[i] = np.random.uniform(5.5, 9.0)
            
    temp_crit = temp_crit.clip(25.0, 120.0)
    oil_crit = oil_crit.clip(10.0, 100.0)
    volt_crit = volt_crit.clip(140.0, 280.0)
    curr_crit = curr_crit.clip(0.6, 14.0)
    labels_crit = np.full(n_critical, 2, dtype=int)
    
    # Combine datasets
    temperatures = np.concatenate([temp_norm, temp_warn, temp_crit])
    oil_levels = np.concatenate([oil_norm, oil_warn, oil_crit])
    voltages = np.concatenate([volt_norm, volt_warn, volt_crit])
    currents = np.concatenate([curr_norm, curr_warn, curr_crit])
    labels = np.concatenate([labels_norm, labels_warn, labels_crit])
    
    df = pd.DataFrame({
        "temperature": np.round(temperatures, 2),
        "oil_level": np.round(oil_levels, 2),
        "voltage": np.round(voltages, 2),
        "current": np.round(currents, 2),
        "health_label": labels
    })
    
    # Feature engineering:
    # 1. Apparent Power (VA) = Voltage * Current
    df["apparent_power"] = np.round(df["voltage"] * df["current"], 2)
    
    # 2. Thermal Stress Index = temperature / (oil_level + 1)
    df["thermal_stress_index"] = np.round(df["temperature"] / (df["oil_level"] + 1e-3), 3)
    
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df

def train_and_export_model():
    print("Generating simulated transformer health dataset...")
    df = generate_transformer_dataset(n_samples=7500, random_state=42)
    
    feature_cols = ["temperature", "oil_level", "voltage", "current", "apparent_power", "thermal_stress_index"]
    X = df[feature_cols]
    y = df["health_label"]
    
    class_names = ["NORMAL", "WARNING", "CRITICAL"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    print(f"Training Random Forest Classifier on {len(X_train)} samples...")
    # Random Forest with 120 decision trees, balanced estimators
    rf_model = RandomForestClassifier(
        n_estimators=120,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5)
    
    print(f"\nModel Evaluation:")
    print(f"Test Accuracy: {accuracy * 100:.2f}%")
    print(f"5-Fold CV Mean Accuracy: {cv_scores.mean() * 100:.2f}% (std: {cv_scores.std() * 100:.2f}%)")
    
    print("\nClassification Report:")
    report_dict = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    
    # Feature Importances
    importances = dict(zip(feature_cols, [round(float(val), 4) for val in rf_model.feature_importances_]))
    print("Feature Importances:", importances)
    
    # Save Model
    joblib.dump(rf_model, MODEL_FILE)
    print(f"Saved Random Forest Model to {MODEL_FILE}")
    
    # Save Metadata for Dashboard display
    metadata = {
        "model_name": "Random Forest Classifier",
        "n_estimators": 120,
        "max_depth": 10,
        "features": feature_cols,
        "class_names": class_names,
        "accuracy": round(float(accuracy), 4),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "confusion_matrix": conf_matrix,
        "feature_importances": importances,
        "classification_report": {
            k: v for k, v in report_dict.items() if isinstance(v, dict)
        },
        "total_training_samples": len(df)
    }
    
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved Model Metadata to {METADATA_FILE}")
    
    # Save a sample CSV for documentation / review presentation reference
    csv_sample_path = os.path.join(MODEL_DIR, "transformer_telemetry_sample.csv")
    df.head(100).to_csv(csv_sample_path, index=False)
    print(f"Saved Sample Dataset to {csv_sample_path}")
    
    return rf_model, metadata

if __name__ == "__main__":
    train_and_export_model()
