import os
import glob
from pathlib import Path

OUT_DIR = os.path.expanduser("~/CreationStudio/outputs")


def scan_outputs(category="all"):
    """Scan output directories and return file paths grouped by type."""
    results = {"images": [], "logos": [], "sprites": [], "audio": [], "video": []}

    patterns = {
        "images": "images/*.{png,jpg,jpeg}",
        "logos": "logos/*.{png,jpg,svg,pdf,zip}",
        "sprites": "sprites/*.png",
        "audio": "audio/**/*.{wav,mp3,ogg}",
        "video": "video/*.{mp4,gif,webm}",
    }

    for key, pattern in patterns.items():
        if category != "all" and category != key:
            continue
        full_pattern = os.path.join(OUT_DIR, pattern)
        # Use pathlib for recursive glob
        base = Path(OUT_DIR)
        for ext_pattern in pattern.split("{")[1].rstrip("}").split(",") if "{" in pattern else [pattern.split(".")[-1]]:
            sub_path = pattern.split("*.")[0] if "*." in pattern else pattern.split("/")[0] + "/"
            sub_path = sub_path.replace("**", "").strip("/")
            search_dir = base / sub_path if sub_path else base
            if search_dir.exists():
                for f in search_dir.rglob(f"*.{ext_pattern}"):
                    results[key].append(str(f))

    # Sort each category by modification time (newest first)
    for key in results:
        results[key].sort(key=lambda x: os.path.getmtime(x), reverse=True)

    return results


def get_image_gallery():
    """Get all images for Gradio gallery display."""
    results = scan_outputs("images")
    sprites = scan_outputs("sprites")
    all_images = results.get("images", []) + sprites.get("sprites", [])
    all_images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return all_images[:50]  # Limit to 50 most recent


def get_audio_files():
    """Get all audio files."""
    results = scan_outputs("audio")
    return results.get("audio", [])[:30]


def get_video_files():
    """Get all video files."""
    results = scan_outputs("video")
    return results.get("video", [])[:20]
