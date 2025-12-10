@echo off
echo ================================================================================
echo EV Power Train Simulation Tool - Build Executable
echo ================================================================================
echo.

echo Step 1: Installing PyInstaller (if not already installed)...
pip install pyinstaller

echo.
echo Step 2: Building executable...
echo This may take 2-5 minutes...
echo.

pyinstaller --name="EV_Simulation_Tool" ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "README.md;." ^
    --hidden-import=numpy ^
    --hidden-import=pandas ^
    --hidden-import=matplotlib ^
    --hidden-import=openpyxl ^
    --collect-all PyQt6 ^
    --collect-all matplotlib ^
    main_app.py

echo.
echo ================================================================================
echo Build Complete!
echo ================================================================================
echo.
echo Your executable is located at:
echo   dist\EV_Simulation_Tool.exe
echo.
echo File size: ~150-200 MB (includes all dependencies)
echo.
echo You can now distribute this single .exe file to anyone!
echo No Python installation required on target machine.
echo.
pause
