@echo off
setlocal enabledelayedexpansion

set LOGFILE=install_log.txt
set PROJECT_DIR=%~dp0

echo =========================================
echo [ARAS-Drive] Setup
echo =========================================
echo.

REM === STEP 1: Python ===
echo [1/3] Checking Python...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo        Python not found. Installing...
    
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%PROJECT_DIR%python-installer.exe'"
    
    if exist "%PROJECT_DIR%python-installer.exe" (
        start /wait "" "%PROJECT_DIR%python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1
        del "%PROJECT_DIR%python-installer.exe"
        echo [OK] Python installed
    ) else (
        echo [ERROR] Failed to download Python
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
) else (
    echo [OK] Python ready
)

REM === STEP 2: Ollama ===
echo [2/3] Checking Ollama...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo        Ollama not found. Installing...
    
    powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%PROJECT_DIR%OllamaSetup.exe'"
    
    if exist "%PROJECT_DIR%OllamaSetup.exe" (
        start /wait "" "%PROJECT_DIR%OllamaSetup.exe" /silent
        del "%PROJECT_DIR%OllamaSetup.exe"
        echo [OK] Ollama installed
    ) else (
        echo [ERROR] Failed to download Ollama
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
) else (
    echo [OK] Ollama ready
)

REM === STEP 3: Python Packages ===
echo [3/3] Installing packages...
python -m pip install --user requests python-telegram-bot >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] requests
    echo [OK] python-telegram-bot
) else (
    echo [ERROR] Failed to install packages
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo.
echo =========================================
echo [SUCCESS] Done!
echo =========================================
echo.
echo Press any key to exit...
pause >nul
