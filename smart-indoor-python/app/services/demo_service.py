from typing import Dict, Any
from app.simulation.scenario_manager import scenario_manager

class DemoService:
    def trigger_scenario(self, hall_id: str, scenario: str) -> Dict[str, Any]:
        result = scenario_manager.set_scenario(hall_id, scenario)
        return {
            "success": True,
            "current_scenario": scenario,
            "hall_id": hall_id,
            "message": f"Demo scenario '{scenario}' successfully activated for hall {hall_id}.",
            "applied_parameters": result
        }

    def get_status(self, hall_id: str) -> str:
        return scenario_manager.get_current_scenario(hall_id)

demo_service = DemoService()
