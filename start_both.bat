@echo off
echo ========================================
echo Starting ATS Resume Generator
echo ========================================
echo.

echo Starting Backend Server...
cd /d "%~dp0backend"
start "Resume Generator - Backend" cmd /k python app.py

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
cd /d "%~dp0frontend"
start "Resume Generator - Frontend" cmd /k python -m http.server 8000

echo.
echo ========================================
echo Servers Started!
echo ========================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:8000
echo.
echo Opening browser...
timeout /t 2 /nobreak > nul
start http://localhost:8000
echo.
echo Press any key to stop all servers...
pause > nul

echo.
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Resume Generator - Backend*" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq Resume Generator - Frontend*" /F > nul 2>&1
echo Done!

