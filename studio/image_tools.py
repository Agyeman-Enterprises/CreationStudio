import os
import datetime
import numpy as np
from PIL import Image

OUT_DIR = os.path.expanduser("~/CreationStudio/outputs")


def upscale_image(image, scale=4):
    """Upscale image using Real-ESRGAN."""
    if image is None:
        return None
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from .device import DEVICE

        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        upsampler = RealESRGANer(
            scale=4,
            model_path=None,  # uses default
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
            gpu_id=0 if DEVICE == "cuda" else None,
        )
        img_array = np.array(image)
        output, _ = upsampler.enhance(img_array, outscale=scale)
        result = Image.fromarray(output)
    except ImportError:
        # Fallback: simple Lanczos upscale
        print("[Upscale] Real-ESRGAN not available, using Lanczos fallback")
        w, h = image.size
        result = image.resize((w * scale, h * scale), Image.LANCZOS)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, "images", f"upscaled_{ts}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    result.save(path)
    return result


def remove_background(image):
    """Remove background using rembg."""
    if image is None:
        return None
    try:
        from rembg import remove
        result = remove(image)
    except ImportError:
        print("[RemoveBG] rembg not available")
        return image

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, "images", f"nobg_{ts}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    result.save(path)
    return result


def img2img(image, prompt, negative_prompt, model_name, denoise_strength, steps, cfg):
    """Image-to-image transformation using SDXL."""
    if image is None:
        return None
    from diffusers import StableDiffusionXLImg2ImgPipeline
    from .device import DEVICE, DTYPE
    import torch

    model_path = os.path.join(
        os.path.expanduser("~/CreationStudio/ComfyUI/models/checkpoints"), model_name
    )
    print(f"[Img2Img] Loading {model_name}...")
    pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
        model_path, torch_dtype=DTYPE, use_safetensors=True
    )
    pipe = pipe.to(DEVICE)
    pipe.enable_attention_slicing()
    pipe.enable_vae_tiling()

    # Ensure image is RGB and proper size
    image = image.convert("RGB").resize((1024, 1024), Image.LANCZOS)

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=image,
        strength=float(denoise_strength),
        num_inference_steps=int(steps),
        guidance_scale=float(cfg),
    ).images[0]

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, "images", f"img2img_{ts}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    result.save(path)
    return result


def stitch_sprite_sheet(images, cols, padding=0):
    """Stitch multiple images into a sprite sheet grid."""
    if not images or len(images) == 0:
        return None

    pil_images = []
    for img in images:
        if isinstance(img, str):
            pil_images.append(Image.open(img))
        elif isinstance(img, np.ndarray):
            pil_images.append(Image.fromarray(img))
        else:
            pil_images.append(img)

    cols = int(cols)
    rows = (len(pil_images) + cols - 1) // cols

    # Normalize sizes to first image
    w, h = pil_images[0].size
    pil_images = [img.resize((w, h), Image.LANCZOS) for img in pil_images]

    sheet_w = cols * w + (cols - 1) * padding
    sheet_h = rows * h + (rows - 1) * padding
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for i, img in enumerate(pil_images):
        r, c = divmod(i, cols)
        x = c * (w + padding)
        y = r * (h + padding)
        sheet.paste(img.convert("RGBA"), (x, y))

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, "sprites", f"spritesheet_{ts}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    return sheet


def make_seamless_tile(image):
    """Make an image seamlessly tileable by blending edges."""
    if image is None:
        return None

    img = image.convert("RGB")
    arr = np.array(img, dtype=np.float32)
    h, w, c = arr.shape
    blend = min(h, w) // 4

    result = arr.copy()

    # Horizontal blend
    for i in range(blend):
        alpha = i / blend
        result[:, i] = arr[:, i] * alpha + arr[:, w - blend + i] * (1 - alpha)
        result[:, w - blend + i] = arr[:, w - blend + i] * alpha + arr[:, i] * (1 - alpha)

    # Vertical blend
    for i in range(blend):
        alpha = i / blend
        result[i, :] = result[i, :] * alpha + result[h - blend + i, :] * (1 - alpha)
        result[h - blend + i, :] = result[h - blend + i, :] * alpha + result[i, :] * (1 - alpha)

    result = Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUT_DIR, "sprites", f"tile_{ts}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    result.save(path)
    return result
