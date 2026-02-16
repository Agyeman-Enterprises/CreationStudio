# Creation Studio

AI-powered image, music, and video generation suite. Built for game dev and social media content creation.

## Features
- **Image Gen** - SDXL text-to-image with model switching, export as PNG/JPG/SVG/PDF
- **Image Tools** - 4x upscale, background removal, img2img, sprite sheet stitching, seamless tiles
- **Audio Lab** - BGM, SFX, ambient generation with looping, chaining, WAV/MP3/OGG export
- **Video Gen** - AI video with social media presets (TikTok, Reels, YouTube, etc.)
- **Gallery** - Browse all generated content

## Quick Start

### Mac
```bash
chmod +x launch.sh
./launch.sh
```

### Windows (PC)
1. Run `setup_pc.bat` once to install dependencies
2. Run `launch.bat` to start

### Manual Setup
```bash
python -m venv studio-venv
source studio-venv/bin/activate  # Mac/Linux
# studio-venv\Scripts\activate   # Windows

# Mac (MPS)
pip install torch torchvision torchaudio

# PC (CUDA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# All platforms
pip install diffusers transformers accelerate gradio
pip install Pillow numpy scipy opencv-python-headless
pip install rembg pydub img2pdf

python studio_app.py
```

Opens at http://127.0.0.1:7860

## SDXL Models
Place `.safetensors` model files in `ComfyUI/models/checkpoints/` (or update MODEL_DIR in `studio/image_gen.py`).
