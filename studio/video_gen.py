import os
import datetime
import subprocess
import torch

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
        from diffusers import WanPipeline
        from .device import DEVICE, DTYPE

        print("[VideoGen] Loading Wan 2.1 T2V-1.3B...")
        _pipe = WanPipeline.from_pretrained(
            "Wan-AI/Wan2.1-T2V-1.3B",
            torch_dtype=DTYPE,
        )
        if DEVICE == "cuda":
            _pipe.enable_model_cpu_offload()
        else:
            _pipe = _pipe.to(DEVICE)
        print("[VideoGen] Wan 2.2 ready!")
    return _pipe


def _resolve_dimensions(preset, custom_w, custom_h):
    """Get target (width, height) from preset or custom values."""
    if preset == "Custom" and custom_w and custom_h:
        w, h = int(custom_w), int(custom_h)
    elif preset in SOCIAL_PRESETS and SOCIAL_PRESETS[preset]:
        w, h = SOCIAL_PRESETS[preset]
    else:
        return None, None
    # Ensure even dimensions
    return w if w % 2 == 0 else w + 1, h if h % 2 == 0 else h + 1


def _postprocess_video(raw_path, final_path, target_w, target_h, fps, output_format):
    """Use ffmpeg to resize and convert video format."""
    try:
        cmd = ["ffmpeg", "-y", "-i", raw_path]
        if target_w and target_h:
            cmd += [
                "-vf",
                f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2",
            ]

        if output_format == "gif":
            cmd += ["-vf", f"fps={fps},scale=480:-1:flags=lanczos", final_path]
        elif output_format == "webm":
            cmd += ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", final_path]
        else:  # mp4
            cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "23", final_path]

        subprocess.run(cmd, check=True, capture_output=True)
        os.unlink(raw_path)
        return final_path
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[VideoGen] ffmpeg error: {e}, returning raw file")
        return raw_path


def generate_video(prompt, num_frames, guidance_scale, fps, preset, output_format, custom_w=None, custom_h=None):
    """Generate a single video clip."""
    from diffusers.utils import export_to_video

    pipeline = load_pipeline()

    # Wan 2.2 1.3B works best at 480p
    gen_height, gen_width = 480, 832

    video = pipeline(
        prompt=prompt,
        num_frames=int(num_frames),
        guidance_scale=float(guidance_scale),
        height=gen_height,
        width=gen_width,
        num_inference_steps=30,
    ).frames[0]

    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fps = int(fps)

    raw_path = os.path.join(OUT_DIR, f"raw_{ts}.mp4")
    export_to_video(video, raw_path, fps=fps)

    target_w, target_h = _resolve_dimensions(preset, custom_w, custom_h)
    output_format = output_format.lower()
    final_path = os.path.join(OUT_DIR, f"video_{ts}.{output_format}")
    final_path = _postprocess_video(raw_path, final_path, target_w, target_h, fps, output_format)

    print(f"[VideoGen] Saved to {final_path}")
    return final_path


def generate_video_chain(prompts_text, frames_each, guidance_scale, fps, preset, output_format, crossfade_frames, custom_w=None, custom_h=None):
    """Generate multiple video clips from newline-separated prompts and stitch them."""
    from diffusers.utils import export_to_video

    prompts = [p.strip() for p in prompts_text.strip().split("\n") if p.strip()]
    if not prompts:
        return None

    pipeline = load_pipeline()
    gen_height, gen_width = 480, 832
    fps = int(fps)
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    clip_paths = []
    for i, prompt in enumerate(prompts):
        print(f"[VideoGen] Generating clip {i+1}/{len(prompts)}: {prompt[:60]}...")

        video = pipeline(
            prompt=prompt,
            num_frames=int(frames_each),
            guidance_scale=float(guidance_scale),
            height=gen_height,
            width=gen_width,
            num_inference_steps=30,
        ).frames[0]

        clip_path = os.path.join(OUT_DIR, f"clip_{ts}_{i:02d}.mp4")
        export_to_video(video, clip_path, fps=fps)
        clip_paths.append(clip_path)

    # Stitch clips with ffmpeg concat
    if len(clip_paths) == 1:
        stitched_raw = clip_paths[0]
    else:
        concat_file = os.path.join(OUT_DIR, f"concat_{ts}.txt")
        with open(concat_file, "w") as f:
            for cp in clip_paths:
                f.write(f"file '{cp}'\n")

        stitched_raw = os.path.join(OUT_DIR, f"stitched_raw_{ts}.mp4")
        try:
            crossfade_sec = float(crossfade_frames) / fps if crossfade_frames > 0 else 0

            if crossfade_sec > 0 and len(clip_paths) > 1:
                # Build complex ffmpeg filter for crossfade
                inputs = []
                for cp in clip_paths:
                    inputs += ["-i", cp]

                filter_parts = []
                prev = "[0:v]"
                for i in range(1, len(clip_paths)):
                    out = f"[v{i}]" if i < len(clip_paths) - 1 else "[vout]"
                    filter_parts.append(
                        f"{prev}[{i}:v]xfade=transition=fade:duration={crossfade_sec}:offset={i * (int(frames_each)/fps - crossfade_sec)}{out}"
                    )
                    prev = out

                cmd = ["ffmpeg", "-y"] + inputs + [
                    "-filter_complex", ";".join(filter_parts),
                    "-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                    stitched_raw,
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            else:
                # Simple concat
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", stitched_raw],
                    check=True, capture_output=True,
                )

            # Clean up clips
            for cp in clip_paths:
                os.unlink(cp)
            os.unlink(concat_file)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"[VideoGen] ffmpeg stitch error: {e}, returning first clip")
            stitched_raw = clip_paths[0]

    # Final resize + format conversion
    target_w, target_h = _resolve_dimensions(preset, custom_w, custom_h)
    output_format = output_format.lower()
    final_path = os.path.join(OUT_DIR, f"chain_{ts}.{output_format}")
    final_path = _postprocess_video(stitched_raw, final_path, target_w, target_h, fps, output_format)

    print(f"[VideoGen] Chain saved to {final_path}")
    return final_path
