from typing import Any, Dict, Optional
from app.engines.base import BaseEngine

class RULEngine(BaseEngine):
    def __init__(self):
        super().__init__("RULEngine")

    async def process(self, current_damage: float, damage_rate: float, max_damage: float = 1.0) -> Dict[str, Any]:
        """
        Calculates RUL based on remaining damage capacity.
        """
        remaining_capacity = max(0.0, max_damage - current_damage)
        
        # Stability: Handle zero or negative rates (which shouldn't happen in physical accumulation)
        if damage_rate <= 0:
            rul = 99999.0 # Effectively infinity for the controller
        else:
            rul = remaining_capacity / damage_rate
            
        # Confidence score modulation
        # Logic: Confidence decays if the damage rate is highly erratic or if data is stale
        confidence = 1.0
        if damage_rate > (raw_damage_delta := 0.001): # Arbitrary threshold for high stress
             confidence = 0.85 # High stress reduces confidence in linear projection
             
        return {
            "rul": rul,
            "confidence": confidence,
            "remaining_capacity": remaining_capacity
        }
