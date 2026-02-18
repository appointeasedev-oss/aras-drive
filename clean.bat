@echo off
setlocal enabledelayedexpansion

set PROJECT_DIR=%~dp0

echo =========================================
echo [ARAS-Drive] Cleanup
echo =========================================
echo.

set /p CONFIRM="Remove packages? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo [CANCELLED]
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 0
)

echo.
echo [INFO] Removing packages...
python -m pip uninstall -y requests python-telegram-bot >nul 2>&1
echo [OK] Done

echo.
echo Press any key to exit...
pause >nul
