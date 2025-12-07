@echo off
REM Quick Git Push Script for Windows
REM This script stages all changes, commits, and pushes to GitHub

echo.
echo ============================================
echo   Quick Git Push to GitHub
echo ============================================
echo.

REM Check if there are any changes
git status --short
if errorlevel 1 (
    echo Error: Not a git repository
    pause
    exit /b 1
)

echo.
echo Staging all changes...
git add .

echo.
echo Enter commit message (or press Enter for default):
set /p commit_msg="Commit message: "

if "%commit_msg%"=="" (
    set commit_msg=Auto-update: Changes pushed on %date% at %time%
)

echo.
echo Committing with message: %commit_msg%
git commit -m "%commit_msg%"

if errorlevel 1 (
    echo.
    echo No changes to commit or commit failed.
    echo.
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub (origin main)...
git push origin main

if errorlevel 1 (
    echo.
    echo Push failed! Please check your connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Successfully pushed to GitHub!
echo ============================================
echo.
pause
