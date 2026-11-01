@echo off
chcp 65001 >nul 2>&1
title 🎬 Remove Watermark Tool

:: ============================================================
:: Drag and drop video files or folders onto this .bat file
:: to remove the Gemini Notebook watermark (last 3.1 seconds)
:: ============================================================

:: Find Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Python not found! Install Python and add it to PATH.
    echo.
    pause
    exit /b 1
)

:: Find ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: FFmpeg not found! Install FFmpeg and add it to PATH.
    echo.
    pause
    exit /b 1
)

:: Get the directory where this .bat file is located
set "SCRIPT_DIR=%~dp0"

:: Process the dropped files/folders, or this script's folder when nothing was dropped
if "%~1"=="" (
    echo.
    echo  No files/folders were dropped. Processing current folder...
    echo.
    python "%SCRIPT_DIR%remove_watermark.py" "%SCRIPT_DIR%"
) else (
    python "%SCRIPT_DIR%remove_watermark.py" %*
)
