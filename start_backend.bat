@echo off
echo Starting LexIndia Backend...

:: Ensure we are in the backend directory
cd backend

:: Activate python venv
call ..\.venv\Scripts\activate.bat

:: Start the FastAPI server using uvicorn
echo Starting FastAPI on http://localhost:8000
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
