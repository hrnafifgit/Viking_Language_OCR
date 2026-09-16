@echo off
title Viking Epigraphy Web AI Platform
cd /d "%~dp0"
echo ============================================================
echo   Starting Viking Epigraphy AI Web Testing Platform...
echo   Model: Full Precision Float32 (1024x1024) + 4-Way TTA
echo ============================================================
echo.
python run_web_app.py
pause
