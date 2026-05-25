@echo off
title H-Dex Ultra Dashboard Launcher
echo [+] Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed! Please install Python 3.x and add it to PATH.
    pause
    exit /b
)

echo [+] Installing/Updating Dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [+] Starting Admin Dashboard...
python admin_dashboard.py
if %errorlevel% neq 0 (
    echo [!] Dashboard crashed with exit code %errorlevel%
    pause
)
pause