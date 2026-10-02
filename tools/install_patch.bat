@echo off
chcp 65001 >nul
title Gunman Contracts FR - install patch
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0apply_french_patch.py" %*
) else (
  python "%~dp0apply_french_patch.py" %*
)
echo.
pause
