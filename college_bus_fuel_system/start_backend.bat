@echo off
title College Bus Fuel Management - Backend REST API
echo ========================================================
echo  Starting College Bus Fuel Backend REST API (Port 5000)
echo ========================================================
cd /d "%~dp0backend"
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo [!] Virtual environment not found. Please run: python -m venv venv and pip install -r requirements.txt
    pause
    exit /b 1
)
python run.py
if %errorlevel% neq 0 (
    echo [ERROR] Backend service exited with error code %errorlevel%.
)
pause
