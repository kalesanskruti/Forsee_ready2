import random
import asyncio
from typing import Dict, Any
from app.engines.base import BaseEngine

class SimulationEngine(BaseEngine):
    def __init__(self):
        super().__init__("SimulationEngine")

    async def generate_synthetic_load(self, asset_type: str) -> Dict[str, Any]:
        """
        Generates realistic synthetic telemetry based on asset type.
        """
        # Base parameters
        base_load = 50.0
        base_temp = 40.0
        
        if asset_type == "Pump":
            load = base_load + random.uniform(0, 20)
            temp = base_temp + (load * 0.2)
        elif asset_type == "Turbine":
            load = base_load + random.uniform(40, 60)
            temp = base_temp + (load * 0.5)
        else:
            load = base_load + random.uniform(0, 5)
            temp = base_temp + (load * 0.1)
            
        return {
            "load": load,
            "temp": temp,
            "timestamp": "now" # In real use, use datetime.utcnow().isoformat()
        }

    async def run_simulation_step(self, asset_id: str, asset_type: str):
        telemetry = await self.generate_synthetic_load(asset_type)
        telemetry["asset_id"] = asset_id
        return telemetry
