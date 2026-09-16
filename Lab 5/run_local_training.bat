@echo off
title Viking Rune Local Fine-Tuning
cd /d "%~dp0"
echo =======================================================================
echo          Viking Rune YOLOv8 - Local Fine-Tuning Launcher
echo =======================================================================
echo.
python train_local_finetune.py --stage1-epochs 15 --stage2-epochs 20 --batch 8 --workers 2
echo.
echo =======================================================================
echo Training process completed.
echo =======================================================================
pause
