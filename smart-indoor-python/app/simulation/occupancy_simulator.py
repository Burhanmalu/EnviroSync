import random
from typing import Dict, Any

class OccupancySimulator:
    """
    Occupancy count and spatial distribution simulator.
    """

    def __init__(self, hall_id: str, capacity: int = 50):
        self.hall_id = hall_id
        self.capacity = capacity
        self.current_people = 18
        self.target_people = 18

    def set_scenario_targets(self, scenario: str):
        if scenario == "HIGH_OCCUPANCY":
            self.target_people = int(self.capacity * 0.88)
        elif scenario == "LOW_OCCUPANCY":
            self.target_people = int(self.capacity * 0.08)
        elif scenario == "HIGH_TEMPERATURE" or scenario == "HIGH_CO2":
            self.target_people = int(self.capacity * 0.65)
        else:  # NORMAL
            self.target_people = int(self.capacity * 0.38)

    def step(self) -> Dict[str, Any]:
        # Step smoothly towards target
        if self.current_people < self.target_people:
            step_size = random.randint(1, 3)
            self.current_people = min(self.target_people, self.current_people + step_size)
        elif self.current_people > self.target_people:
            step_size = random.randint(1, 3)
            self.current_people = max(self.target_people, self.current_people - step_size)
        else:
            # Minor fluctuation
            self.current_people += random.choice([-1, 0, 1])

        self.current_people = max(0, min(self.capacity, self.current_people))
        pct = round((self.current_people / self.capacity) * 100.0, 1)

        # Distribute into 4 room zones
        if self.current_people > 0:
            z_a = int(round(self.current_people * 0.35))
            z_b = int(round(self.current_people * 0.30))
            z_c = int(round(self.current_people * 0.20))
            z_d = max(0, self.current_people - (z_a + z_b + z_c))
        else:
            z_a, z_b, z_c, z_d = 0, 0, 0, 0

        return {
            "people_count": self.current_people,
            "occupancy_percentage": pct,
            "capacity": self.capacity,
            "zone_distribution": {
                "Zone A": z_a,
                "Zone B": z_b,
                "Zone C": z_c,
                "Zone D": z_d
            }
        }
