@echo off@echo off

echo.echo Starting Genoscope Frontend Server...

echo ====================================echo.

echo    Starting GenoScope Frontend

echo ====================================REM Check for Python installation

echo.where python >nul 2>nul

if %ERRORLEVEL% neq 0 (

cd src\frontend    echo Python not found. Please install Python to run this application.

    pause

echo Frontend will open at: http://localhost:8080    exit /b 1

echo Backend should be running at: http://localhost:8000)

echo.

echo Press Ctrl+C to stop the serverecho Starting a simple HTTP server on port 8080...

echo.echo.

echo Frontend will be available at: http://localhost:8080

python -m http.server 8080echo.

echo IMPORTANT: Make sure the backend server is running at http://localhost:8000
echo To start the backend, run: run_genoscope.bat
echo.
echo Press Ctrl+C to stop the server
echo.

cd frontend
python -m http.server 8080

pause