@echo off
title College Bus Driver Mobile App - Flutter
echo ========================================================
echo  Launching Flutter Driver Mobile Application
echo ========================================================
cd /d "%~dp0driver_app"

where flutter >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Flutter SDK not found in system PATH.
    echo Please install Flutter or add its bin directory to PATH.
    pause
    exit /b 1
)

echo Checking connected Flutter devices...
flutter devices

if "%~1" neq "" (
    echo Running on specified device: %~1
    flutter run -d %~1
) else (
    echo Launching application on available device...
    flutter run
)

if %errorlevel% neq 0 (
    echo [ERROR] Flutter run exited with error code %errorlevel%.
)
pause
