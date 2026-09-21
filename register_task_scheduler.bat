@echo off
:: ================================================================
::  World SORFIX — Register Windows Task Scheduler
::  Run this ONCE as Administrator to auto-start on boot/login.
::  After running, World SORFIX will start at 7:01 AM every day
::  AND every time you log in.
:: ================================================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please right-click this file and choose "Run as Administrator"
    pause
    exit /b 1
)

set TASK_NAME=World SORFIX - Auto Start
set APP_DIR=%~dp0
set SCRIPT=%APP_DIR%start.bat

echo Registering Task: %TASK_NAME%
echo Script: %SCRIPT%
echo.

:: Delete old task if it exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Register: run at login + daily at 07:01
schtasks /create /tn "%TASK_NAME%" /tr "cmd /c \"%SCRIPT%\"" /sc onlogon /rl highest /f
if %errorlevel% equ 0 (
    echo [OK] World SORFIX registered to start on login.
) else (
    echo [FAIL] Could not register on-login task.
)

schtasks /create /tn "%TASK_NAME% - Daily 0701" /tr "cmd /c \"%SCRIPT%\"" /sc daily /st 07:01 /rl highest /f
if %errorlevel% equ 0 (
    echo [OK] World SORFIX also registered to start daily at 07:01.
) else (
    echo [FAIL] Could not register daily task.
)

echo.
echo Done. World SORFIX will now start automatically.
echo Portal: http://localhost:9091/portal
pause
