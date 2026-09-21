@echo off
setlocal enabledelayedexpansion

:: ================================================================
::  Pan SORFIX  —  Morning Startup Script
::
::  What this does:
::    1. Kills any stale process already holding port 9090
::    2. Activates virtualenv if one exists
::    3. Starts the server (logs go to logs\app.log + console)
::    4. Auto-restarts up to MAX_RESTARTS times if it crashes
::
::  To run at startup automatically, use:
::    register_task_scheduler.bat
:: ================================================================

set APP_NAME=Pan SORFIX
set PORT=9090
set MAX_RESTARTS=5
set RESTART_DELAY_S=3
set APP_DIR=%~dp0

title %APP_NAME%
cd /d "%APP_DIR%"

:: Activate virtualenv if present (app-level or parent-level)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

:KILL_OLD
:: Kill any stale process already holding the port
echo [%date% %time%] Clearing port %PORT%...
for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":%PORT% "') do (
    echo   Killing PID %%p on port %PORT%
    taskkill /F /PID %%p 2>nul
)
timeout /t 2 /nobreak >nul

set RESTARTS=0

:LOOP
set /a RESTARTS+=1
if !RESTARTS! gtr %MAX_RESTARTS% (
    echo.
    echo [%date% %time%] ERROR: %APP_NAME% failed to start after %MAX_RESTARTS% attempts.
    echo Check logs\app.log for details.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo  %APP_NAME%   Attempt !RESTARTS!/%MAX_RESTARTS%   %date% %time%
echo ================================================================
python main.py

set EXIT_CODE=!ERRORLEVEL!
if !EXIT_CODE! equ 0 (
    echo [%date% %time%] %APP_NAME% exited cleanly.
    exit /b 0
)

echo [%date% %time%] %APP_NAME% crashed (exit code !EXIT_CODE!). Restarting in %RESTART_DELAY_S%s...
timeout /t %RESTART_DELAY_S% /nobreak >nul
goto :LOOP
