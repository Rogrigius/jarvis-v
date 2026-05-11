@echo off
echo Starting JARVIS...
if not exist "venv" (
    echo [ERROR] Virtual environment not found. Please run install.bat first.
    pause
    exit /b
)

call venv\Scripts\activate
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] JARVIS crashed or failed to start.
    pause
)
