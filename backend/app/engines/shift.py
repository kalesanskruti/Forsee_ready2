from typing import Any, Dict
from app.engines.base import BaseEngine

class ShiftEngine(BaseEngine):
    def __init__(self):
        super().__init__("ShiftEngine")

    async def process(self, telemetry: Dict[str, Any], config: Dict[str, Any]) -> float:
        """
        Detects shift violations and returns a damage multiplier.
        config: {'threshold_load': float, 'penalty_weight': float}
        """
        load = telemetry.get("load", 0.0)
        threshold = config.get("threshold_load", 100.0)
        penalty_weight = config.get("penalty_weight", 0.5)
        
        multiplier = 1.0
        if load > threshold:
            violation_ratio = load / threshold
            # industrial calculation: Bounded penalty to prevent instability
            multiplier = 1.0 + (violation_ratio - 1.0) * penalty_weight
            multiplier = min(5.0, multiplier)
            
            self.log_event(
                telemetry.get("asset_id", "unknown"),
                f"Violation detected! Load: {load:.2f} > Threshold: {threshold:.2f}. Multiplier: {multiplier:.3f}",
                level="WARNING"
            )
            
        return multiplier
