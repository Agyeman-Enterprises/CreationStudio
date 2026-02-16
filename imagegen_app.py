import gradio as gr
import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import os
import glob

MODEL_DIR = os.path.expanduser("~/CreationStudio/ComfyUI/models/checkpoints")

def get_models():
    models = glob.glob(os.path.join(MODEL_DIR, "*.safetensors"))
    return [os.path.basename(m) for m in models]

pipe = None
current_model_name = None

def load_model(model_name):
    global pipe, current_model_name
    if model_name != current_model_name:
        model_path = os.path.join(MODEL_DIR, model_name)
        print(f"Loading {model_name}...")
        pipe = StableDiffusionXLPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float32,
            use_safetensors=True
        )
        if torch.backends.mps.is_available():
            pipe = pipe.to("mps")
            print("Using Apple Silicon GPU (MPS)")
        pipe.enable_attention_slicing()
        pipe.enable_vae_tiling()
        current_model_name = model_name
        print(f"{model_name} loaded!")
    return pipe

def generate(prompt, negative_prompt, model_name, width, height, steps, cfg, seed):
    pipeline = load_model(model_name)
    generator = torch.Generator()
    if seed > 0:
        generator = generator.manual_seed(seed)

    image = pipeline(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=cfg,
        generator=generator,
    ).images[0]

    return image

models = get_models()
default_model = next((m for m in models if "Juggernaut" in m), models[0]) if models else "sd_xl_base_1.0.safetensors"

with gr.Blocks(title="Image Gen", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Image Gen")
    gr.Markdown("Generate images from text using SDXL models on your M1 Max.")

    with gr.Row():
        with gr.Column(scale=1):
            prompt = gr.Textbox(label="Prompt", lines=3, placeholder="a cinematic photo of a mountain lake at sunrise, golden light, mist rising, 8k")
            negative = gr.Textbox(label="Negative Prompt", value="ugly, deformed, blurry, low quality, watermark, text, jpeg artifacts")
            model = gr.Dropdown(choices=models, value=default_model, label="Model")

            with gr.Row():
                width = gr.Slider(512, 1536, 1024, step=64, label="Width")
                height = gr.Slider(512, 1536, 1024, step=64, label="Height")

            with gr.Row():
                steps = gr.Slider(10, 50, 25, step=1, label="Steps")
                cfg = gr.Slider(1, 15, 7, step=0.5, label="CFG Scale")

            seed = gr.Number(label="Seed (0 = random)", value=0)
            btn = gr.Button("Generate", variant="primary", size="lg")

        with gr.Column(scale=1):
            output = gr.Image(label="Result", type="pil")

    btn.click(fn=generate, inputs=[prompt, negative, model, width, height, steps, cfg, seed], outputs=output)

demo.launch(server_name="0.0.0.0", server_port=7862)
