@echo off
setlocal enabledelayedexpansion

set PROJECT_DIR=%~dp0
set BOT_TOKEN=8499443906:AAEOuGKja1BiY0n5BhjlBKTaQGm6OyDCM3Q
set USER_ID=5732751751
set OLLAMA_PATH=C:\Users\satvi\AppData\Local\Programs\Ollama\ollama.exe

echo =========================================
echo [ARAS] AI Agent by SS Corporations
echo =========================================
echo.

REM Check Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Run setup.bat first.
    pause
    exit /b 1
)

REM Check packages
python -c "import telegram" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Packages missing. Run setup.bat first.
    pause
    exit /b 1
)

REM Check Ollama
if exist "%OLLAMA_PATH%" (
    set OLLAMA=%OLLAMA_PATH%
) else (
    where ollama >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Ollama not found. Run setup.bat first.
        pause
        exit /b 1
    )
)

echo [1] Starting Ollama...
start "Ollama" cmd /c "ollama serve"
timeout /t 3 /nobreak >nul

REM Get available models
echo [2] Available models:
echo.

powershell -Command "$r = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 5; $i = 1; $r.models | ForEach-Object { Write-Host \"  [$i] $($_.name)\"; $i++ }"

echo.
set /p MODEL_NUM="Select model number: "

for /f "delims=" %%m in ('powershell -Command "$r = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 5; $r.models[%MODEL_NUM%-1].name"') do set SELECTED_MODEL=%%m

if "%SELECTED_MODEL%"=="" (
    echo [ERROR] Invalid selection.
    pause
    exit /b 1
)

echo.
echo =========================================
echo [3] Choose Interface
echo =========================================
echo.
echo   [1] Telegram    - Chat via Telegram bot
echo   [2] Local       - Chat in command prompt
echo   [3] Both        - Run Telegram + Local together
echo.
set /p INTERFACE="Select (1/2/3): "

if "%INTERFACE%"=="1" goto :telegram
if "%INTERFACE%"=="2" goto :local
if "%INTERFACE%"=="3" goto :both

echo [ERROR] Invalid selection.
pause
exit /b 1

:telegram
echo.
echo =========================================
echo [READY] Starting ARAS on Telegram
echo =========================================
echo   Bot Token: %BOT_TOKEN:~0,10%...
echo   User ID: %USER_ID%
echo   Model: %SELECTED_MODEL%
echo.
echo Press any key to start...
pause >nul

start "ARAS Telegram" cmd /k "cd /d %PROJECT_DIR%agent && python telegram_agent.py %BOT_TOKEN% %USER_ID% %SELECTED_MODEL%"
exit /b 0

:local
echo.
echo =========================================
echo [READY] Starting ARAS Local Chat
echo =========================================
echo   Model: %SELECTED_MODEL%
echo   Workspace: %PROJECT_DIR%workspace
echo.
echo Press any key to start...
pause >nul

start "ARAS Local" cmd /k "cd /d %PROJECT_DIR%agent && python local_chat.py %SELECTED_MODEL%"
exit /b 0

:both
echo.
echo =========================================
echo [READY] Starting ARAS on Telegram + Local
echo =========================================
echo   Bot Token: %BOT_TOKEN:~0,10%...
echo   User ID: %USER_ID%
echo   Model: %SELECTED_MODEL%
echo.
echo Press any key to start...
pause >nul

echo Starting Telegram bot...
start "ARAS Telegram" cmd /k "cd /d %PROJECT_DIR%agent && python telegram_agent.py %BOT_TOKEN% %USER_ID% %SELECTED_MODEL%"

timeout /t 2 /nobreak >nul

echo Starting Local chat...
start "ARAS Local" cmd /k "cd /d %PROJECT_DIR%agent && python local_chat.py %SELECTED_MODEL%"

exit /b 0
