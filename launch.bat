@echo off
cd /d "%~dp0"
py -3 launch.py 2>nul || python launch.py 2>nul || python3 launch.py
if errorlevel 1 (
    echo.
    echo  Python not found. Install from https://python.org
    pause
)
