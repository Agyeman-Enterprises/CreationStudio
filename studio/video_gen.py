import os
import datetime
import subprocess

OUT_DIR = os.path.expanduser("~/CreationStudio/outputs/video")

_pipe = None

SOCIAL_PRESETS = {
    "Instagram Reels / TikTok (9:16)": (1080, 1920),
    "Instagram Post (1:1)": (1080, 1080),
    "YouTube Shorts (9:16)": (1080, 1920),
    "YouTube / Twitter (16:9)": (1920, 1080),
    "Custom": None,
}


def load_pipeline():
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import CogVideoXPipeline
        from .device import DEVICE

        print("[VideoGen] Loading CogVideoX-2b...")
        _pipe = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-2b", torch_dtype=torch.float16
        )
        _pipe.enable_model_cpu_offload()
        print("[VideoGen] CogVideoX ready!")
    return _pipe


def generate_video(prompt, num_frames, guidance_scale, fps, preset, output_format, custom_w=None, custom_h=None):
    """Generate video with social media preset support."""
    from diffusers.utils import export_to_video

    pipeline = load_pipeline()
    video = pipeline(
        prompt=prompt,
        num_videos_per_prompt=1,
        num_inference_steps=50,
        num_frames=int(num_frames),
        guidance_scale=float(guidance_scale),
    ).frames[0]

    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fps = int(fps)

    # Export raw video
    raw_path = os.path.join(OUT_DIR, f"raw_{ts}.mp4")
    export_to_video(video, raw_path, fps=fps)

    # Get target dimensions
    if preset == "Custom" and custom_w and custom_h:
        target_w, target_h = int(custom_w), int(custom_h)
    elif preset in SOCIAL_PRESETS and SOCIAL_PRESETS[preset]:
        target_w, target_h = SOCIAL_PRESETS[preset]
    else:
        # No resize needed
        target_w, target_h = None, None

    output_format = output_format.lower()
    final_path = os.path.join(OUT_DIR, f"video_{ts}.{output_format}")

    # Use ffmpeg for resize + format conversion
    try:
        cmd = ["ffmpeg", "-y", "-i", raw_path]
        if target_w and target_h:
            # Ensure even dimensions
            target_w = target_w if target_w % 2 == 0 else target_w + 1
            target_h = target_h if target_h % 2 == 0 else target_h + 1
            cmd += ["-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"]

        if output_format == "gif":
            cmd += ["-vf", f"fps={fps},scale=480:-1:flags=lanczos", final_path]
        elif output_format == "webm":
            cmd += ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", final_path]
        else:  # mp4
            cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "23", final_path]

        subprocess.run(cmd, check=True, capture_output=True)
        os.unlink(raw_path)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[VideoGen] ffmpeg error: {e}, returning raw file")
        final_path = raw_path

    print(f"[VideoGen] Saved to {final_path}")
    return final_path
