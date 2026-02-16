import torch
import os
import glob
from diffusers import StableDiffusionXLPipeline
from .device import DEVICE, DTYPE

MODEL_DIR = os.path.expanduser("~/CreationStudio/ComfyUI/models/checkpoints")

_pipe = None
_current_model = None


def get_models():
    """Scan checkpoints directory for available models."""
    models = glob.glob(os.path.join(MODEL_DIR, "*.safetensors"))
    names = [os.path.basename(m) for m in models]
    return sorted(names) if names else ["No models found"]


def get_default_model():
    models = get_models()
    return next((m for m in models if "Juggernaut" in m), models[0])


def load_model(model_name):
    global _pipe, _current_model
    if model_name == _current_model and _pipe is not None:
        return _pipe
    model_path = os.path.join(MODEL_DIR, model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    print(f"[ImageGen] Loading {model_name}...")
    _pipe = StableDiffusionXLPipeline.from_single_file(
        model_path, torch_dtype=DTYPE, use_safetensors=True
    )
    _pipe = _pipe.to(DEVICE)
    _pipe.enable_attention_slicing()
    _pipe.enable_vae_tiling()
    _current_model = model_name
    print(f"[ImageGen] {model_name} loaded on {DEVICE}")
    return _pipe


def generate(prompt, negative_prompt, model_name, width, height, steps, cfg, seed):
    """Generate an image from text prompt."""
    pipeline = load_model(model_name)
    generator = torch.Generator(device="cpu")
    if seed > 0:
        generator = generator.manual_seed(int(seed))

    image = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=int(width),
        height=int(height),
        num_inference_steps=int(steps),
        guidance_scale=float(cfg),
        generator=generator,
    ).images[0]

    # Save to outputs
    import datetime
    out_dir = os.path.expanduser("~/CreationStudio/outputs/images")
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"img_{ts}.png")
    image.save(path)
    print(f"[ImageGen] Saved to {path}")

    return image
