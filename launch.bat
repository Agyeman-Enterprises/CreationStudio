@echo off
REM ============================================
REM  Creation Studio - Windows Launcher
REM  Double-click this to start. That's it.
REM ============================================
cd /d "%~dp0"

echo.
echo  ========================================
echo   Creation Studio
echo  ========================================
echo.

REM Pull latest code
echo  [1/4] Pulling latest...
git pull 2>nul
if errorlevel 1 echo  (skipped - not a git repo or no remote)

REM Check if venv exists, create if not
if not exist "studio-venv\Scripts\activate.bat" (
    echo  [2/4] First run - setting up environment...
    echo         This takes a few minutes. Grab coffee.
    echo.

    REM Find Python 3.10
    py -3.10 --version >nul 2>&1
    if errorlevel 1 (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo  ERROR: Python not found.
            echo  Install Python 3.10 from python.org
            pause
            exit /b 1
        )
        python -m venv studio-venv
    ) else (
        py -3.10 -m venv studio-venv
    )

    call studio-venv\Scripts\activate.bat

    echo  Installing PyTorch with CUDA...
    pip install --upgrade pip >nul 2>&1
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

    echo  Installing AI models + dependencies...
    pip install gradio>=6.0 fastapi uvicorn
    pip install diffusers transformers accelerate
    pip install parler-tts audiocraft
    pip install Pillow numpy scipy opencv-python-headless
    pip install rembg[gpu] pydub img2pdf
    pip install realesrgan basicsr

    echo.
    echo  Setup complete!
    echo.
) else (
    echo  [2/4] Environment ready
    call studio-venv\Scripts\activate.bat
)

echo  [3/4] Starting server...

REM Open browser after server boots
start /b cmd /c "timeout /t 10 >nul && start http://127.0.0.1:7860"

echo  [4/4] Opening browser...
echo.
echo  Local:   http://127.0.0.1:7860
echo  Network: Check terminal output for LAN IP
echo  PWA:     Install via browser menu on any device
echo  ========================================
echo.

python studio_app.py
