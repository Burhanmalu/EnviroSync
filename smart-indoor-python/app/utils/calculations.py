import math
from typing import Dict, Any

def calculate_heat_index(temp_c: float, humidity: float) -> float:
    """Calculate perceived temperature in Celsius using NOAA approximation."""
    # Convert to Fahrenheit
    t_f = (temp_c * 9.0 / 5.0) + 32.0
    rh = humidity

    # Simple formula first
    hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))

    # If > 80F, use Rothfusz regression equation
    if hi_f >= 80.0:
        hi_f = (
            -42.379
            + 2.04901523 * t_f
            + 10.14333127 * rh
            - 0.22475541 * t_f * rh
            - 0.00683783 * t_f * t_f
            - 0.05481717 * rh * rh
            + 0.00122874 * t_f * t_f * rh
            + 0.00085282 * t_f * rh * rh
            - 0.00000199 * t_f * t_f * rh * rh
        )

    # Convert back to Celsius
    return round((hi_f - 32.0) * 5.0 / 9.0, 1)

def calculate_iaq_score(co2: float, humidity: float, temperature: float) -> Dict[str, Any]:
    """Calculate Indoor Air Quality (IAQ) sub-score and status."""
    # CO2 component (0-100)
    if co2 <= 600:
        co2_sub = 100 - (co2 - 400) * 0.05
    elif co2 <= 1000:
        co2_sub = 90 - (co2 - 600) * 0.05
    elif co2 <= 1500:
        co2_sub = 70 - (co2 - 1000) * 0.06
    else:
        co2_sub = max(20.0, 40.0 - (co2 - 1500) * 0.04)

    # Humidity component (ideal 40-60%)
    if 45.0 <= humidity <= 55.0:
        hum_sub = 100.0
    elif 40.0 <= humidity <= 60.0:
        hum_sub = 90.0
    elif 30.0 <= humidity <= 70.0:
        hum_sub = 70.0
    else:
        hum_sub = 40.0

    score = int(round(co2_sub * 0.7 + hum_sub * 0.3))
    score = max(0, min(100, score))

    if score >= 85:
        status = "EXCELLENT"
    elif score >= 70:
        status = "GOOD"
    elif score >= 50:
        status = "MODERATE"
    else:
        status = "POOR"

    return {
        "iaq_score": score,
        "iaq_status": status,
        "co2_sub": int(round(co2_sub)),
        "humidity_sub": int(round(hum_sub))
    }
