@echo off
REM Creation Studio Launcher (Windows)
cd /d "%~dp0"

echo Starting Creation Studio...

REM Activate venv
call studio-venv\Scripts\activate.bat

REM Open browser after server starts
start /b cmd /c "timeout /t 10 >nul && start http://127.0.0.1:7860"

python studio_app.py
