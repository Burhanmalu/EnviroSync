from typing import Dict, Any

class ComfortScorer:
    """
    Multi-parameter System Comfort Scorer.
    Calculates overall room comfort index from 0 to 100 based on
    thermal, atmospheric, air quality, visual, and spatial crowding inputs.
    """

    @staticmethod
    def calculate(
        temperature: float,
        humidity: float,
        co2: float,
        occupancy_pct: float,
        light: float
    ) -> Dict[str, Any]:
        # 1. Temperature Score (Optimal: 23°C - 26°C)
        if 23.0 <= temperature <= 26.0:
            temp_score = 100.0 - abs(temperature - 24.5) * 5.0
        elif 20.0 <= temperature < 23.0:
            temp_score = 90.0 - (23.0 - temperature) * 12.0
        elif 26.0 < temperature <= 29.0:
            temp_score = 90.0 - (temperature - 26.0) * 12.0
        else:
            temp_score = max(20.0, 54.0 - abs(temperature - 24.5) * 8.0)

        # 2. Humidity Score (Optimal: 45% - 55%)
        if 45.0 <= humidity <= 55.0:
            hum_score = 100.0 - abs(humidity - 50.0) * 1.5
        elif 40.0 <= humidity < 45.0 or 55.0 < humidity <= 65.0:
            hum_score = 85.0 - abs(humidity - 50.0) * 1.8
        else:
            hum_score = max(20.0, 60.0 - abs(humidity - 50.0) * 2.0)

        # 3. Air Quality (CO2) Score (Optimal: < 600 ppm)
        if co2 <= 600:
            co2_score = 100.0 - (co2 - 400.0) * 0.05
        elif co2 <= 1000:
            co2_score = 90.0 - (co2 - 600.0) * 0.05
        elif co2 <= 1500:
            co2_score = 70.0 - (co2 - 1000.0) * 0.06
        else:
            co2_score = max(15.0, 40.0 - (co2 - 1500.0) * 0.03)

        # 4. Occupancy Score (Optimal: 20% - 75%)
        if 20.0 <= occupancy_pct <= 75.0:
            occ_score = 95.0
        elif occupancy_pct < 20.0:
            occ_score = 85.0  # Underutilized
        elif 75.0 < occupancy_pct <= 90.0:
            occ_score = 75.0 - (occupancy_pct - 75.0) * 2.0
        else:
            occ_score = max(20.0, 45.0 - (occupancy_pct - 90.0) * 3.5)

        # 5. Light Score (Optimal: 350 - 650 lux)
        if 350.0 <= light <= 650.0:
            light_score = 95.0
        elif 200.0 <= light < 350.0:
            light_score = 85.0 - (350.0 - light) * 0.1
        elif 650.0 < light <= 850.0:
            light_score = 85.0 - (light - 650.0) * 0.1
        else:
            light_score = max(30.0, 65.0 - abs(light - 500.0) * 0.05)

        # Clamp all subscores to [0, 100]
        temp_score = int(round(max(0.0, min(100.0, temp_score))))
        hum_score = int(round(max(0.0, min(100.0, hum_score))))
        co2_score = int(round(max(0.0, min(100.0, co2_score))))
        occ_score = int(round(max(0.0, min(100.0, occ_score))))
        light_score = int(round(max(0.0, min(100.0, light_score))))

        # Weighted Overall Comfort Index
        # Weights: Temp 30%, CO2 25%, Humidity 20%, Occupancy 15%, Light 10%
        overall = (
            temp_score * 0.30 +
            co2_score * 0.25 +
            hum_score * 0.20 +
            occ_score * 0.15 +
            light_score * 0.10
        )
        final_score = int(round(max(0.0, min(100.0, overall))))

        if final_score >= 85:
            status = "EXCELLENT"
        elif final_score >= 70:
            status = "GOOD"
        elif final_score >= 55:
            status = "FAIR"
        else:
            status = "POOR"

        return {
            "score": final_score,
            "status": status,
            "temperature_score": temp_score,
            "humidity_score": hum_score,
            "air_quality_score": co2_score,
            "occupancy_score": occ_score,
            "light_score": light_score,
            "disclaimer": "System Comfort Score - calculated using multi-parameter environmental indexing"
        }

comfort_scorer = ComfortScorer()
