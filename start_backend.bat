@echo off
echo Starting Optical Fiber Simulation Backend...
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if venv exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment and run the backend
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the backend
echo Starting backend server...
python run_backend.py

REM Deactivate virtual environment when done
call venv\Scripts\deactivate.bat

pause 