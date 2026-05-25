@echo off
title H-Dex HF Server Local Test
echo [INFO] Installing requirements...
pip install -r requirements.txt
echo [INFO] Starting Server on port 7860...
python app.py
pause
