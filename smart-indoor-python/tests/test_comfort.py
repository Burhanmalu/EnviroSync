import pytest
from app.ai.comfort.scorer import comfort_scorer
from app.ai.comfort.predictor import prediction_ai

def test_comfort_scorer_ranges():
    # Ideal conditions
    result = comfort_scorer.calculate(
        temperature=24.5,
        humidity=50.0,
        co2=450.0,
        occupancy_pct=40.0,
        light=500.0
    )
    assert result["score"] >= 85
    assert result["status"] == "EXCELLENT"
    assert "disclaimer" in result

    # Extreme conditions
    harsh_result = comfort_scorer.calculate(
        temperature=35.0,
        humidity=88.0,
        co2=2200.0,
        occupancy_pct=98.0,
        light=1200.0
    )
    assert harsh_result["score"] < 50
    assert harsh_result["status"] == "POOR"

def test_prediction_service_forecasting():
    forecast = prediction_ai.predict_future_metrics(
        current_temp=26.0,
        current_humidity=55.0,
        current_co2=600.0,
        occupancy_count=40,
        ac_power=False,
        horizon_minutes=20
    )
    assert "predictions" in forecast
    assert forecast["predictions"]["temperature"]["predicted"] > 26.0
    assert forecast["confidence"] > 70.0
