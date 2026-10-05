import random
import math
import time
from typing import Dict, Any

class SensorSimulator:
    """
    Realistic environmental sensor simulator.
    Uses gradual Brownian drift with sinusoidal diurnal variations
    to prevent unnatural random telemetry jumps.
    """

    def __init__(self, hall_id: str):
        self.hall_id = hall_id
        # State values
        self.temperature = 25.4
        self.humidity = 52.0
        self.co2 = 540.0
        self.light = 450.0

        # Targets according to scenario
        self.target_temperature = 25.0
        self.target_humidity = 50.0
        self.target_co2 = 550.0
        self.target_light = 450.0

    def set_scenario_targets(self, scenario: str):
        if scenario == "HIGH_TEMPERATURE":
            self.target_temperature = 31.5
            self.target_humidity = 68.0
            self.target_co2 = 720.0
            self.target_light = 650.0
        elif scenario == "HIGH_OCCUPANCY":
            self.target_temperature = 28.5
            self.target_humidity = 64.0
            self.target_co2 = 1450.0
            self.target_light = 700.0
        elif scenario == "HIGH_CO2":
            self.target_temperature = 26.8
            self.target_humidity = 58.0
            self.target_co2 = 1680.0
            self.target_light = 500.0
        elif scenario == "LOW_OCCUPANCY":
            self.target_temperature = 23.5
            self.target_humidity = 44.0
            self.target_co2 = 420.0
            self.target_light = 200.0
        else:  # NORMAL
            self.target_temperature = 24.8
            self.target_humidity = 50.0
            self.target_co2 = 560.0
            self.target_light = 450.0

    def step(self, ac_power: bool = True, fan_speed: int = 2) -> Dict[str, float]:
        """
        Advance simulated physics by one time step with smooth gradual convergence.
        """
        # Dynamic drift rates
        temp_step = 0.08
        co2_step = 15.0
        hum_step = 0.3
        light_step = 10.0

        # Adjust target if AC is actively cooling
        effective_temp_target = self.target_temperature
        if ac_power:
            effective_temp_target -= 1.5

        # 1. Temperature gradual drift
        if self.temperature < effective_temp_target:
            self.temperature += min(temp_step, (effective_temp_target - self.temperature) * 0.1)
        elif self.temperature > effective_temp_target:
            self.temperature -= min(temp_step, (self.temperature - effective_temp_target) * 0.1)
        self.temperature += (random.random() - 0.5) * 0.04

        # 2. Humidity gradual drift
        if self.humidity < self.target_humidity:
            self.humidity += min(hum_step, (self.target_humidity - self.humidity) * 0.1)
        elif self.humidity > self.target_humidity:
            self.humidity -= min(hum_step, (self.humidity - self.target_humidity) * 0.1)
        self.humidity += (random.random() - 0.5) * 0.15

        # 3. CO2 gradual drift
        if self.co2 < self.target_co2:
            self.co2 += min(co2_step, (self.target_co2 - self.co2) * 0.1)
        elif self.co2 > self.target_co2:
            self.co2 -= min(co2_step, (self.co2 - self.target_co2) * 0.1)
        self.co2 += (random.random() - 0.5) * 5.0

        # 4. Light gradual drift
        if self.light < self.target_light:
            self.light += min(light_step, (self.target_light - self.light) * 0.1)
        elif self.light > self.target_light:
            self.light -= min(light_step, (self.light - self.target_light) * 0.1)
        self.light += (random.random() - 0.5) * 4.0

        # Clamp to realistic ranges
        self.temperature = round(max(20.0, min(36.0, self.temperature)), 1)
        self.humidity = round(max(30.0, min(90.0, self.humidity)), 1)
        self.co2 = round(max(380.0, min(2500.0, self.co2)), 1)
        self.light = round(max(50.0, min(1500.0, self.light)), 1)

        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2": self.co2,
            "light": self.light
        }
