@echo off
title Launch Viking Rune Epigraphy AI (App + Server)
cd /d "%~dp0"

echo ======================================================================
echo   Viking Rune Epigraphy AI - System Launcher
echo ======================================================================

:: 1. Check if backend is already listening on port 5000
netstat -ano | findstr ":5000" >nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Backend server is already active on port 5000.
) else (
    echo [..] Starting Backend Server in background...
    start "Viking AI Backend Server" cmd /c "python backend_api.py"
    timeout /t 3 /nobreak >nul
)

:: 2. Launch Flutter App
echo [..] Launching Viking Rune Flutter App...
cd /d "%~dp0viking_rune_app\build\windows\x64\runner\Debug"
start "" "viking_rune_app.exe"

echo [OK] Application launched successfully!
exit /b 0
