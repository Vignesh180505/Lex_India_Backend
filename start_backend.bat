@echo off
echo =========================================
echo  LexIndia Backend Launcher
echo =========================================

:: Kill any process already using port 8000
echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo Killing PID %%a on port 8000...
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: Move into backend directory
cd /d "%~dp0backend"

:: Activate venv
call ..\\.venv\Scripts\activate.bat

:: Start FastAPI server
echo.
echo Starting FastAPI on http://localhost:8000 ...
echo Press Ctrl+C to stop.
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
