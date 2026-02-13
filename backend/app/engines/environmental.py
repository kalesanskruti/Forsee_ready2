from typing import Any, Dict
from app.engines.base import BaseEngine

class EnvironmentalEngine(BaseEngine):
    def __init__(self):
        super().__init__("EnvironmentalEngine")

    async def process(self, context: Dict[str, Any]) -> float:
        """
        Calculates environmental modifier based on humidity, temperature, etc.
        """
        temp = context.get("ambient_temp", 25.0)
        humidity = context.get("humidity", 50.0)
        
        # Basal aging rate (Arrhenius-like simplified logic)
        aging_factor = 1.0 + (max(0, temp - 25) * 0.01) + (max(0, humidity - 70) * 0.02)
        
        # Bounded to avoid unrealistic scaling
        aging_factor = min(2.0, aging_factor)
        
        return aging_factor
