from abc import ABC, abstractmethod
from typing import Any, Dict
from loguru import logger

class BaseEngine(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def process(self, data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Main processing loop for the engine.
        'data' usually contains telemetry or previous engine output.
        'context' contains tenant_id and asset_id.
        """
        pass

    def log_event(self, asset_id: str, message: str, level: str = "INFO"):
        logger.opt(depth=1).log(level, f"[{self.name}] Asset {asset_id}: {message}")
