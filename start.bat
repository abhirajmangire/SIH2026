@echo off
title SIH 2026 - Identity Screening System
echo =============================================
echo   SIH 2026 - AI Fake Identity Screening
echo   Problem Statement ID: 26188
echo =============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+
    echo Download from: https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    echo Download from: https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

echo.
echo Setting up backend...
cd backend

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate venv and install dependencies
call venv\Scripts\activate.bat
echo Installing Python dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

REM Start backend in new window
start "SIH Backend" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && python main.py"

cd ..

echo.
echo Setting up frontend...
cd frontend

echo Installing Node dependencies...
npm install --silent
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node dependencies
    pause
    exit /b 1
)

echo.
echo =============================================
echo   Starting SIH 2026 Demo...
echo =============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Demo Credentials:
echo   Officer ID: OFFICER001
echo   Password:   SecurePass123!
echo.
echo Press Ctrl+C in the backend window to stop.
echo =============================================

REM Start frontend
start "SIH Frontend" cmd /k "cd /d %CD% && npm run dev"

cd ..
echo.
echo Both servers starting... Please wait a moment.
echo Open http://localhost:5173 in your browser.
pause