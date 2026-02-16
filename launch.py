#!/usr/bin/env python3
"""
Creation Studio — Universal Launcher
Detects Mac/Windows/Linux, sets up everything, launches.
Double-click launch.bat (Windows) or launch.command (Mac).
"""
import os
import sys
import platform
import subprocess
import shutil

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(STUDIO_DIR)

IS_WIN = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

VENV_DIR = os.path.join(STUDIO_DIR, "studio-venv")
VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe") if IS_WIN else os.path.join(VENV_DIR, "bin", "python")
VENV_PIP = os.path.join(VENV_DIR, "Scripts", "pip.exe") if IS_WIN else os.path.join(VENV_DIR, "bin", "pip")


def banner(msg):
    print(f"\n  {'='*48}")
    print(f"   {msg}")
    print(f"  {'='*48}\n")


def step(n, total, msg):
    print(f"  [{n}/{total}] {msg}")


def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=isinstance(cmd, str), **kwargs)


def git_pull():
    """Pull latest changes if this is a git repo."""
    if os.path.isdir(os.path.join(STUDIO_DIR, ".git")):
        step(1, 4, "Pulling latest...")
        result = run("git pull", capture_output=True, text=True)
        if result.returncode != 0:
            print("         (no remote or offline — skipped)")
    else:
        step(1, 4, "Not a git repo — skipping pull")


def find_python():
    """Find a suitable Python 3.10-3.12 on the system."""
    candidates = ["python3.10", "python3.11", "python3.12", "python3"]
    if IS_WIN:
        # Windows py launcher
        for minor in [10, 11, 12]:
            candidates.insert(0, f"py,-3.{minor}")
        candidates.append("python")

    for candidate in candidates:
        try:
            if candidate.startswith("py,"):
                cmd = candidate.split(",")
            else:
                cmd = [candidate]
            result = subprocess.run(
                cmd + ["--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                ver = result.stdout.strip().split()[-1]  # "Python 3.10.x" -> "3.10.x"
                parts = ver.split(".")
                major, minor = int(parts[0]), int(parts[1])
                if major == 3 and 10 <= minor <= 12:
                    print(f"         Found Python {ver}")
                    return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            continue
    return None


def setup_venv():
    """Create venv and install all dependencies."""
    banner("First Run — Setting Up")
    print("  This takes a few minutes. Grab coffee.\n")

    python_cmd = find_python()
    if not python_cmd:
        print("  ERROR: Python 3.10-3.12 not found!")
        if IS_WIN:
            print("  Install from: https://www.python.org/downloads/")
            print("  Make sure to check 'Add to PATH' during install")
        elif IS_MAC:
            print("  Install with: brew install python@3.10")
            print("  Or download from: https://www.python.org/downloads/")
        input("\n  Press Enter to exit...")
        sys.exit(1)

    # Create venv
    print("  Creating virtual environment...")
    run(python_cmd + ["-m", "venv", VENV_DIR])

    # Upgrade pip
    run([VENV_PIP, "install", "--upgrade", "pip"], capture_output=True)

    # Install PyTorch (platform-specific)
    if IS_WIN:
        print("  Installing PyTorch + CUDA (for NVIDIA GPU)...")
        run([VENV_PIP, "install", "torch", "torchvision", "torchaudio",
             "--index-url", "https://download.pytorch.org/whl/cu128"])
    elif IS_MAC:
        print("  Installing PyTorch (MPS acceleration on Apple Silicon)...")
        run([VENV_PIP, "install", "torch", "torchvision", "torchaudio"])
    else:
        print("  Installing PyTorch (CPU)...")
        run([VENV_PIP, "install", "torch", "torchvision", "torchaudio",
             "--index-url", "https://download.pytorch.org/whl/cpu"])

    # Install everything else
    print("  Installing AI models + dependencies...")
    run([VENV_PIP, "install", "gradio>=6.0", "fastapi", "uvicorn"])
    run([VENV_PIP, "install", "diffusers", "transformers", "accelerate"])
    run([VENV_PIP, "install", "parler-tts", "audiocraft"])
    run([VENV_PIP, "install", "Pillow", "numpy", "scipy", "opencv-python-headless"])
    if IS_WIN:
        run([VENV_PIP, "install", "rembg[gpu]", "pydub", "img2pdf"])
    else:
        run([VENV_PIP, "install", "rembg", "pydub", "img2pdf"])
    run([VENV_PIP, "install", "realesrgan", "basicsr"])

    print("\n  Setup complete!\n")


def open_browser():
    """Open browser once the server is up."""
    import threading
    import time

    def _wait_and_open():
        import urllib.request
        for _ in range(60):
            try:
                urllib.request.urlopen("http://127.0.0.1:7860", timeout=2)
                break
            except Exception:
                time.sleep(1)
        # Open browser
        if IS_WIN:
            os.system("start http://127.0.0.1:7860")
        elif IS_MAC:
            os.system("open http://127.0.0.1:7860")
        else:
            os.system("xdg-open http://127.0.0.1:7860 2>/dev/null")

    t = threading.Thread(target=_wait_and_open, daemon=True)
    t.start()


def main():
    os_name = "Windows" if IS_WIN else "macOS" if IS_MAC else "Linux"
    banner(f"Creation Studio — {os_name}")

    # Step 1: Git pull
    git_pull()

    # Step 2: Setup if needed
    if not os.path.isfile(VENV_PYTHON):
        setup_venv()
    else:
        step(2, 4, "Environment ready")

    # Step 3: Launch server
    step(3, 4, "Starting server...")
    open_browser()
    step(4, 4, "Opening browser...")
    print()
    print("  Local:   http://127.0.0.1:7860")
    print("  PWA:     Install via browser menu on any device")
    print(f"  {'='*48}")
    print()

    # Run with the venv Python
    os.execv(VENV_PYTHON, [VENV_PYTHON, os.path.join(STUDIO_DIR, "studio_app.py")])


if __name__ == "__main__":
    main()
