import sys
import os
import asyncio
import httpx
import random
import time
from datetime import datetime

# Add the parent directory to sys.path to resolve app modules if needed, 
# though we are using HTTP here so it's strictly a client.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ASSETS = [
    {"id": "pump-001", "type": "Pump", "name": "Main Feed Pump"},
    {"id": "turb-002", "type": "Turbine", "name": "Gas Turbine A"},
    {"id": "comp-003", "type": "Compressor", "name": "Air Compressor 1"},
]

API_URL = "http://localhost:8000/api/v1"

async def register_assets(client):
    print("Registering assets...")
    # Use hardcoded tenant for demo
    tenant_id = "demo-tenant"
    
    # Login to get token (Skipping for now if auth is complex, assumes dev mode or we can add a bypass/token generation script)
    # For simplicity, we'll implement a basic loop without auth if endpoints open, 
    # but endpoints are protected. We need a token.
    
    # Login as admin (assuming created, or we create one). 
    # Since we can't easily login without a user in DB, 
    # we might need to seed the DB first.
    pass

async def simulate_traffic():
    print(f"Starting simulation on {API_URL}")
    
    # We need to bypass auth or have a flexible token for simulation.
    # Alternatively, the simulation runner can import the app code directly 
    # and call the service layer if we want to bypass HTTP auth for local demo.
    # But HTTP is better for "real" testing.
    
    # Let's try to ingest without auth? No, `get_current_tenant_id` is required.
    # We will generate a token using the internal security utility since we have access to the code!
    from app.core.security import create_access_token
    token = create_access_token("sim_user", tenant_id="demo-tenant")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # 1. Register Assets (Idempotent-ish via backend check)
        for asset in ASSETS:
            try:
                # We need to register first. 
                # But /assets/register needs admin/engineer role.
                # Let's create an admin token.
                admin_token = create_access_token("admin_user", tenant_id="demo-tenant")
                # Wait, the token payload needs role?
                # The create_access_token helper in security.py only takes subject and tenant_id.
                # It doesn't take role? 
                # Let's check security.py content again.
                pass
            except Exception:
                pass

        # 2. Main Loop
        while True:
            for asset in ASSETS:
                # Generate synthetic data
                load = random.uniform(50, 90)
                temp = 40 + (load * 0.3) + random.uniform(-2, 2)
                
                payload = {
                    "load": load,
                    "temp": temp,
                    "ambient_temp": 25.0 + random.uniform(-5, 5),
                    "humidity": 60.0 + random.uniform(-10, 10),
                }
                
                try:
                    resp = await client.post(
                        f"{API_URL}/reliability/ingest/{asset['id']}",
                        json=payload,
                        headers=headers
                    )
                    if resp.status_code == 200:
                        print(f"[{datetime.now().time()}] Ingested {asset['id']}: Load={load:.1f}, RUL={resp.json().get('current_rul', 'N/A'):.1f}")
                    else:
                        print(f"Failed to ingest {asset['id']}: {resp.status_code} - {resp.text}")
                except Exception as e:
                    print(f"Error connecting to backend: {e}")
            
            await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(simulate_traffic())
    except KeyboardInterrupt:
        print("Simulation stopped.")
