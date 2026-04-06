@echo off
REM LexIndia Project Fresh Start Script
REM Fixes all common startup issues

echo.
echo ========================================
echo    LexIndia - Fresh Start
echo ========================================
echo.

REM Step 1: Kill any running processes
echo [1/6] Stopping old processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

REM Step 2: Clean Python cache
echo [2/6] Cleaning Python cache...
cd /d "%~dp0backend"
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Removing %%d
    rmdir /s /q "%%d"
)

REM Step 3: Install backend dependencies
echo [3/6] Installing backend dependencies...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo Backend dependencies OK

REM Step 4: Initialize database
echo [4/6] Initializing database...
python seed_data.py >nul 2>&1
echo Database seeded

REM Step 5: Generate embeddings
echo [5/6] Generating embeddings...
python setup/generate_embeddings.py >nul 2>&1
echo Embeddings generated

REM Step 6: Start backend
echo [6/6] Starting backend...
echo.
echo ========================================
echo    Backend starting on port 8000
echo    Access: http://localhost:8000
echo ========================================
echo.

cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
