@echo off
echo ==========================================
echo    JARVIS - INSTALLATION SCRIPT
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

REM Create virtual environment
echo [1/3] Creating virtual environment (venv)...
python -m venv venv

REM Activate virtual environment and install dependencies
echo [2/3] Installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create necessary directories
echo [3/3] Setting up directory structure...
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "database" mkdir database
if not exist "assets" mkdir assets
if not exist "plugins" mkdir plugins
if not exist "commands" mkdir commands

echo.
echo ==========================================
echo    INSTALLATION COMPLETE
echo ==========================================
echo To start JARVIS, run run.bat
echo.
pause
