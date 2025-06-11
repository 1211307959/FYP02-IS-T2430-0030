@echo off
echo Starting IDSS (Intelligent Decision Support System)
echo ===================================================

REM Start the Flask API backend with Ethical Time-Enhanced Model
start cmd /k "echo Starting Flask API backend with Ethical Time-Enhanced Model... && python combined_time_enhanced_ethical_api.py"

REM Allow time for the API to start
timeout /t 3 /nobreak

REM Start the Next.js frontend with clean rebuild
echo Cleaning Next.js build cache...
if exist ".next" rmdir /s /q .next
echo Installing dependencies...
start cmd /k "echo Starting Next.js frontend... && npm run dev"

echo Both services are starting...
echo.
echo Access the application at http://localhost:3000
echo. 