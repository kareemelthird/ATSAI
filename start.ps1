# ATS/AI Application - Windows PowerShell Startup Script
# This script helps you start both backend and frontend servers

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  ATS/AI Application Startup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Check if Node modules exist
if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "[ERROR] Frontend node_modules not found!" -ForegroundColor Red
    Write-Host "Please run: cd frontend && npm install" -ForegroundColor Yellow
    exit 1
}

# Check if .env files exist
if (-not (Test-Path ".\backend\.env")) {
    Write-Host "[WARNING] backend/.env not found. Using example configuration." -ForegroundColor Yellow
    Copy-Item ".\backend\.env.example" ".\backend\.env"
}

if (-not (Test-Path ".\frontend\.env")) {
    Write-Host "[WARNING] frontend/.env not found. Using example configuration." -ForegroundColor Yellow
    Copy-Item ".\frontend\.env.example" ".\frontend\.env"
}

Write-Host "[INFO] Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\..\. venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

Write-Host "[INFO] Starting Frontend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Servers Started Successfully!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to stop all servers..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop all servers
Write-Host "Stopping servers..." -ForegroundColor Yellow
Get-Process -Name "python", "node" | Where-Object { $_.Path -like "*ATS*" } | Stop-Process -Force
Write-Host "All servers stopped." -ForegroundColor Green
