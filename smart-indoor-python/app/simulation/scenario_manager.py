import logging
from typing import Dict, Any, Optional
from app.simulation.sensor_simulator import SensorSimulator
from app.simulation.occupancy_simulator import OccupancySimulator

logger = logging.getLogger("smart_indoor.scenarios")

class ScenarioManager:
    """
    Coordinates multi-hall demo scenarios and live telemetry generation.
    Supports: NORMAL, HIGH_TEMPERATURE, HIGH_OCCUPANCY, HIGH_CO2, LOW_OCCUPANCY
    """

    def __init__(self):
        self.active_scenarios: Dict[str, str] = {}
        self.sensor_simulators: Dict[str, SensorSimulator] = {}
        self.occupancy_simulators: Dict[str, OccupancySimulator] = {}

    def get_or_create_simulators(self, hall_id: str, capacity: int = 50):
        if hall_id not in self.sensor_simulators:
            self.sensor_simulators[hall_id] = SensorSimulator(hall_id)
            self.occupancy_simulators[hall_id] = OccupancySimulator(hall_id, capacity)
            self.active_scenarios[hall_id] = "NORMAL"
        return self.sensor_simulators[hall_id], self.occupancy_simulators[hall_id]

    def set_scenario(self, hall_id: str, scenario: str) -> Dict[str, Any]:
        valid_scenarios = ["NORMAL", "HIGH_TEMPERATURE", "HIGH_OCCUPANCY", "HIGH_CO2", "LOW_OCCUPANCY"]
        if scenario not in valid_scenarios:
            raise ValueError(f"Unknown scenario {scenario}. Must be one of {valid_scenarios}")

        sensor_sim, occ_sim = self.get_or_create_simulators(hall_id)
        self.active_scenarios[hall_id] = scenario
        sensor_sim.set_scenario_targets(scenario)
        occ_sim.set_scenario_targets(scenario)

        logger.info(f"Set Scenario for Hall {hall_id}: {scenario}")
        return {
            "hall_id": hall_id,
            "scenario": scenario,
            "target_temperature": sensor_sim.target_temperature,
            "target_co2": sensor_sim.target_co2,
            "target_occupancy_count": occ_sim.target_people
        }

    def get_current_scenario(self, hall_id: str) -> str:
        return self.active_scenarios.get(hall_id, "NORMAL")

scenario_manager = ScenarioManager()
