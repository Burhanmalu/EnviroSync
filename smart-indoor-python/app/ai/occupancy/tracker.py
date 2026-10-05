from typing import List, Dict, Any

class OccupancyTracker:
    """Tracks continuous occupancy trends and inflow/outflow delta over rolling windows."""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.history: List[int] = []

    def update(self, count: int) -> Dict[str, Any]:
        self.history.append(count)
        if len(self.history) > self.window_size:
            self.history.pop(0)

        if len(self.history) >= 2:
            delta = self.history[-1] - self.history[0]
            trend = "INCREASING" if delta > 1 else "DECREASING" if delta < -1 else "STABLE"
        else:
            delta = 0
            trend = "STABLE"

        return {
            "current_count": count,
            "rolling_average": sum(self.history) / len(self.history),
            "trend": trend,
            "net_delta": delta
        }

occupancy_tracker = OccupancyTracker()
