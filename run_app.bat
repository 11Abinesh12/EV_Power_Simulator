@echo off
echo ========================================
echo   EV Power Train Simulation Tool
echo ========================================
echo.
echo Starting application...
echo.

python main_app.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    echo Please ensure Python and all dependencies are installed.
    echo Run: pip install -r requirements.txt
    echo.
    pause
)
