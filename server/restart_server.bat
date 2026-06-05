@echo off
echo ========================================
echo   Restarting Clare & CareIQ Server
echo   With LOCAL Vision Models
echo ========================================
echo.

cd /d "%~dp0"

echo Stopping any existing Python processes...
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

echo.
echo Starting server with vision models...
echo.
echo Expected logs:
echo   - Qwen2-VL model found (PRIMARY)
echo   - Report Processor ready with Vision Service
echo.

python run_dev.py

pause

