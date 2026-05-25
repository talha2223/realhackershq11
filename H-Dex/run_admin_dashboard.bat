@echo off
title Admin Dashboard Launcher
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! Please install Python 3.x and add it to PATH.
    pause
    exit /b
)

echo Installing/Updating Dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Starting Admin Dashboard...
python admin_dashboard.py > dashboard_error.log 2>&1
echo Script finished. Check dashboard_error.log if the app did not open.
pause