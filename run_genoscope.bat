@echo off@echo off

echo.echo Running Genoscope Application

echo ====================================echo ============================

echo      GenoScope - Full Stack

echo ====================================REM Check if virtual environment exists

echo.if not exist .venv (

echo Starting Backend and Frontend...    echo Virtual environment not found. Creating one...

echo.    python -m venv .venv

    call .venv\Scripts\activate

REM Start backend in a new window    echo Installing requirements...

start "GenoScope Backend" cmd /k run_backend.bat    pip install -r backend\requirements.txt

) else (

REM Wait a few seconds for backend to start    echo Activating virtual environment...

timeout /t 5 /nobreak >nul    call .venv\Scripts\activate

)

REM Start frontend in a new window

start "GenoScope Frontend" cmd /k run_frontend.batecho.

echo Starting application...

echo.echo.

echo ====================================

echo   GenoScope is starting!REM Run the application

echo ====================================cd backend

echo.python run_app.py

echo Backend:  http://localhost:8000

echo Frontend: http://localhost:8080REM Deactivate virtual environment when done

echo.cd ..

echo Two command windows will open.call deactivate
echo Close them to stop the servers.
echo.
pause
