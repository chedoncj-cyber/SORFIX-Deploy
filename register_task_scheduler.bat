@echo off
:: ================================================================
::  Pan SORFIX — Register Windows Task Scheduler
::  Run this ONCE as Administrator to auto-start on boot/login.
::  After running, Pan SORFIX will start at 7:00 AM every day
::  AND every time you log in.
:: ================================================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please right-click this file and choose "Run as Administrator"
    pause
    exit /b 1
)

set TASK_NAME=Pan SORFIX - Auto Start
set APP_DIR=%~dp0
set SCRIPT=%APP_DIR%start.bat

echo Registering Task: %TASK_NAME%
echo Script: %SCRIPT%
echo.

:: Delete old task if it exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Register: run at login + daily at 07:00
schtasks /create /tn "%TASK_NAME%" /tr "cmd /c \"%SCRIPT%\"" /sc onlogon /rl highest /f
if %errorlevel% equ 0 (
    echo [OK] Pan SORFIX registered to start on login.
) else (
    echo [FAIL] Could not register on-login task.
)

schtasks /create /tn "%TASK_NAME% - Daily 0700" /tr "cmd /c \"%SCRIPT%\"" /sc daily /st 07:00 /rl highest /f
if %errorlevel% equ 0 (
    echo [OK] Pan SORFIX also registered to start daily at 07:00.
) else (
    echo [FAIL] Could not register daily task.
)

echo.
echo Done. Pan SORFIX will now start automatically.
echo Portal: http://localhost:9090/portal
pause
