@echo off
chcp 65001 >nul
title Gunman Contracts FR - restore original files
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0apply_french_patch.py" --restore %*
) else (
  python "%~dp0apply_french_patch.py" --restore %*
)
echo.
pause
