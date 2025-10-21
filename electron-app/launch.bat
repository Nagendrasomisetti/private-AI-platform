@echo off
REM PrivAI Desktop - Windows Launcher
REM This script launches the PrivAI desktop application

echo.
echo ========================================
echo    PrivAI Desktop Application
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo Checking dependencies...

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing Electron dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if frontend is built
if not exist "..\frontend\build" (
    echo Building frontend...
    cd ..\frontend
    npm install
    npm run build
    cd ..\electron-app
    if %errorlevel% neq 0 (
        echo ERROR: Failed to build frontend
        pause
        exit /b 1
    )
)

REM Check if backend dependencies are installed
if not exist "..\backend\venv" (
    echo Setting up backend...
    cd ..\backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..\electron-app
    if %errorlevel% neq 0 (
        echo ERROR: Failed to setup backend
        pause
        exit /b 1
    )
)

echo.
echo Starting PrivAI Desktop...
echo.

REM Start the application
npm start

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start PrivAI Desktop
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo PrivAI Desktop has been closed.
pause
