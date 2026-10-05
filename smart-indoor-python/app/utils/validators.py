from typing import Tuple

def validate_environment_ranges(
    temperature: float,
    humidity: float,
    co2: float,
    light: float
) -> Tuple[bool, str]:
    if not (-20.0 <= temperature <= 60.0):
        return False, f"Temperature {temperature}°C is outside valid physical range (-20 to 60°C)"
    if not (0.0 <= humidity <= 100.0):
        return False, f"Humidity {humidity}% must be between 0 and 100%"
    if not (300.0 <= co2 <= 5000.0):
        return False, f"CO2 {co2} ppm is outside valid indoor sensor range (300 to 5000 ppm)"
    if not (0.0 <= light <= 50000.0):
        return False, f"Light {light} lux is outside valid range (0 to 50000 lux)"
    return True, "Valid"
