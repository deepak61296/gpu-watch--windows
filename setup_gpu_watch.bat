@echo off
echo Installing GPU Watch dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo Run GPU Watch with: python gpu_watch.py
echo.
pause
