"""
AI Comfort & Environmental Prediction Model Training Script.
Trains Random Forest Regressors for multi-step environmental forecasting.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def generate_synthetic_training_data(n_samples: int = 2000):
    np.random.seed(42)
    # Features: [current_temp, current_humidity, current_co2, occupancy, ac_state, fan_speed]
    temps = np.random.uniform(22.0, 32.0, n_samples)
    hums = np.random.uniform(35.0, 75.0, n_samples)
    co2s = np.random.uniform(400.0, 1600.0, n_samples)
    occs = np.random.randint(0, 60, n_samples)
    ac_states = np.random.choice([0, 1], n_samples)
    fan_speeds = np.random.randint(0, 5, n_samples)

    # Targets after 20 mins:
    target_temps = temps + (occs * 0.04) - (ac_states * 1.5) + np.random.normal(0, 0.2, n_samples)
    target_co2s = co2s + (occs * 12.0) - (fan_speeds * 25.0) + np.random.normal(0, 15.0, n_samples)

    X = np.column_stack([temps, hums, co2s, occs, ac_states, fan_speeds])
    y_temp = target_temps
    y_co2 = target_co2s

    return X, y_temp, y_co2

def train():
    print("Generating training dataset...")
    X, y_temp, y_co2 = generate_synthetic_training_data()

    X_train, X_test, y_train_t, y_test_t = train_test_split(X, y_temp, test_size=0.2, random_state=42)

    print("Fitting Temperature Prediction Model...")
    rf_temp = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    rf_temp.fit(X_train, y_train_t)

    preds_t = rf_temp.predict(X_test)
    r2_t = r2_score(y_test_t, preds_t)
    rmse_t = np.sqrt(mean_squared_error(y_test_t, preds_t))
    print(f"Temperature Model: R2 = {r2_t:.4f}, RMSE = {rmse_t:.4f}°C")

    # Save models
    os.makedirs("ai_models", exist_ok=True)
    joblib.dump(rf_temp, "ai_models/temp_predictor_v1.pkl")
    print("Model serialized to ai_models/temp_predictor_v1.pkl")

if __name__ == "__main__":
    train()
