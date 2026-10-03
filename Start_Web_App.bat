@echo off
chcp 65001 >nul 2>&1
title 🌐 Remove Watermark - Web App

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [X] ERROR: Python not found! Install Python and add it to PATH.
    echo.
    pause
    exit /b 1
)

:: Check FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [X] ERROR: FFmpeg not found! Install FFmpeg and add it to PATH.
    echo.
    pause
    exit /b 1
)

set "SCRIPT_DIR=%~dp0"

echo.
echo  +======================================================+
echo  ^|   Starting Video Watermark Remover Web App...       ^|
echo  ^|   Opening http://localhost:5000 in your browser     ^|
echo  +======================================================+
echo.

python "%SCRIPT_DIR%app.py"
if %errorlevel% neq 0 (
    echo.
    echo  Server stopped with an error.
    pause
)
