<# 
.SYNOPSIS
    SIH 2026 - AI Fake Identity & Document Screening System Startup Script

.DESCRIPTION
    Starts both backend (FastAPI) and frontend (React + Vite) servers for the SIH 2026 demo.

.NOTES
    Problem Statement ID: 26188
    Requires: Python 3.10+, Node.js 18+
#>

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   SIH 2026 - AI Fake Identity Screening" -ForegroundColor Cyan
Write-Host "   Problem Statement ID: 26188" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Python not found" }
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+" -ForegroundColor Red
    Write-Host "Download from: https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Node.js not found" }
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Yellow

Set-Location -Path "backend"

# Create virtual environment if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate venv and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start backend in new window
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; & '.\venv\Scripts\Activate.ps1'; python main.py" -PassThru

Set-Location -Path ".."

Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Yellow

Set-Location -Path "frontend"

Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Node dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Starting SIH 2026 Demo..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Yellow
Write-Host "  Officer ID: OFFICER001" -ForegroundColor White
Write-Host "  Password:   SecurePass123!" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in the backend window to stop." -ForegroundColor Gray
Write-Host "=============================================" -ForegroundColor Cyan

# Start frontend
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev" -PassThru

Set-Location -Path ".."

Write-Host ""
Write-Host "Both servers starting... Please wait a moment." -ForegroundColor Yellow
Write-Host "Open http://localhost:5173 in your browser." -ForegroundColor Green
Write-Host ""
Write-Host "Press Enter to exit this launcher (servers will keep running)..." -ForegroundColor Gray
Read-Host