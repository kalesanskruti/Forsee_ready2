from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TelemetryIngest(BaseModel):
    load: float
    temp: float
    base_damage_factor: Optional[float] = 0.0001
    ambient_temp: Optional[float] = 25.0
    humidity: Optional[float] = 50.0
    extra_data: Optional[Dict[str, Any]] = None
