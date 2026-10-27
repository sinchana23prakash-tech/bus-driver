@echo off
title College Bus Fuel Management - React Admin / VC Dashboard
echo ========================================================
echo  Starting React Admin / VC Dashboard (Port 3000)
echo ========================================================
cd /d "%~dp0frontend"

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm not found in system PATH.
    echo Please install Node.js (https://nodejs.org) to run the React dashboard.
    pause
    exit /b 1
)

if not exist "node_modules\" (
    echo [INFO] node_modules not detected. Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
)

echo Starting Vite development server on port 3000...
call npm run dev
if %errorlevel% neq 0 (
    echo [ERROR] Frontend dev server stopped with error code %errorlevel%.
)
pause
