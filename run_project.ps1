Write-Host "Starting FORSEE Intelligence Platform..." -ForegroundColor Cyan

# 1. Start Backend
Write-Host "Launching Backend Server (Port 8000)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; .venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

# 2. Start Frontend
Write-Host "Launching Frontend (Port 5173)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "npm run dev"

# 3. Start Simulation
Write-Host "Starting Simulation Engine..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "cd backend; .venv/Scripts/python scripts/run_simulation.py"

# 4. Open Browser
Write-Host "Opening Dashboard..." -ForegroundColor White
Start-Process "http://localhost:8080"

Write-Host "All services launched." -ForegroundColor Cyan
