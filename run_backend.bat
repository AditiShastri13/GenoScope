@echo off
echo.
echo ====================================
echo    Starting GenoScope Application
echo ====================================
echo.

REM Navigate to backend
cd src\backend

REM Check if virtual environment exists
if not exist "..\..\venv\" (
    echo Creating virtual environment...
    python -m venv ..\..\venv
)

REM Activate virtual environment
call ..\..\venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start the backend server
echo.
echo Starting backend server on http://localhost:8000
echo.
python run_app.py
