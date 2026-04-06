# LexIndia Project Fresh Start Script (PowerShell)
# Fixes all common startup issues

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   LexIndia - Fresh Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any running processes
Write-Host "[1/6] Stopping old processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Step 2: Clean Python cache
Write-Host "[2/6] Cleaning Python cache..." -ForegroundColor Yellow
$backend_path = "$PSScriptRoot\backend"
Get-ChildItem -Path $backend_path -Directory -Filter __pycache__ -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Step 3: Install backend dependencies
Write-Host "[3/6] Installing backend dependencies..." -ForegroundColor Yellow
$venv_path = "$backend_path\venv"
if (-not (Test-Path $venv_path)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venv_path
}

# Activate venv and install
& "$venv_path\Scripts\Activate.ps1"
pip install -q -r "$backend_path\requirements.txt" | Out-Null
Write-Host "Backend dependencies OK" -ForegroundColor Green

# Step 4: Initialize database
Write-Host "[4/6] Initializing database..." -ForegroundColor Yellow
Set-Location $backend_path
python seed_data.py | Out-Null
Write-Host "Database seeded" -ForegroundColor Green

# Step 5: Generate embeddings
Write-Host "[5/6] Generating embeddings..." -ForegroundColor Yellow
python setup/generate_embeddings.py | Out-Null
Write-Host "Embeddings generated" -ForegroundColor Green

# Step 6: Start backend
Write-Host "[6/6] Starting backend..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Backend starting on port 8000" -ForegroundColor Cyan
Write-Host "   Access: http://localhost:8000" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
