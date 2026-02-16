@echo off
REM Creation Studio - PC Setup Script
REM Run this once on your Windows PC to install everything

echo ==========================================
echo   Creation Studio - PC Setup
echo ==========================================
echo.

REM Check Python
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv studio-venv
call studio-venv\Scripts\activate.bat

echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo Installing dependencies...
pip install diffusers transformers accelerate gradio>=4.0
pip install Pillow numpy scipy opencv-python-headless
pip install rembg[gpu] pydub img2pdf
pip install realesrgan basicsr

echo.
echo ==========================================
echo   Setup complete!
echo   Run launch.bat to start Creation Studio
echo ==========================================
pause
