from prometheus_client import Counter, Gauge, Histogram, generate_latest
from fastapi import Response

# Metrics definitions
PROCESSED_TELEMETRY = Counter("forsee_telemetry_total", "Total processed telemetry packets")
RELIABILITY_SCORE = Gauge("forsee_asset_health", "Current health score per asset", ["tenant_id", "asset_id"])
PROCESSING_TIME = Histogram("forsee_processing_seconds", "Time spent processing reliability logic")

def get_metrics():
    return Response(content=generate_latest(), media_type="text/plain")
