#!/bin/bash
# ============================================
#  Creation Studio - Mac Launcher
#  Double-click this to start. That's it.
# ============================================
STUDIO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$STUDIO_DIR"

echo ""
echo "  ========================================"
echo "   Creation Studio"
echo "  ========================================"
echo ""

# Pull latest code
echo "  [1/4] Pulling latest..."
git pull 2>/dev/null || echo "  (skipped - not a git repo or no remote)"

# Check if venv exists, create if not
if [ ! -f "studio-venv/bin/activate" ]; then
    echo "  [2/4] First run — setting up environment..."
    echo "         This takes a few minutes. Grab coffee."
    echo ""

    # Find best Python (prefer 3.10, accept 3.11/3.12)
    PYTHON=""
    for candidate in python3.10 python3.11 python3.12 python3; do
        if command -v "$candidate" &>/dev/null; then
            ver=$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" = "3" ] && [ "$minor" -ge 10 ] && [ "$minor" -le 12 ]; then
                PYTHON="$candidate"
                echo "  Found $candidate (Python $ver)"
                break
            fi
        fi
    done

    if [ -z "$PYTHON" ]; then
        echo "  ERROR: Python 3.10-3.12 not found."
        echo "  Install from: https://www.python.org/downloads/"
        echo "  Or: brew install python@3.10"
        echo ""
        read -p "  Press Enter to exit..."
        exit 1
    fi

    "$PYTHON" -m venv studio-venv
    source studio-venv/bin/activate

    echo "  Installing PyTorch..."
    pip install --upgrade pip >/dev/null 2>&1
    # Mac: MPS acceleration on Apple Silicon, CPU on Intel — auto-detected
    pip install torch torchvision torchaudio

    echo "  Installing AI models + dependencies..."
    pip install "gradio>=6.0" fastapi uvicorn
    pip install diffusers transformers accelerate
    pip install parler-tts audiocraft
    pip install Pillow numpy scipy opencv-python-headless
    pip install rembg pydub img2pdf
    pip install realesrgan basicsr

    echo ""
    echo "  Setup complete!"
    echo ""
else
    echo "  [2/4] Environment ready"
    source studio-venv/bin/activate
fi

echo "  [3/4] Starting server..."

# Open browser once server is up
(while ! curl -s http://127.0.0.1:7860 >/dev/null 2>&1; do sleep 1; done
 open "http://127.0.0.1:7860" 2>/dev/null || xdg-open "http://127.0.0.1:7860" 2>/dev/null) &

echo "  [4/4] Opening browser..."
echo ""
echo "  Local:   http://127.0.0.1:7860"
echo "  Network: Check terminal output for LAN IP"
echo "  PWA:     Install via browser menu on any device"
echo "  ========================================"
echo ""

python studio_app.py
