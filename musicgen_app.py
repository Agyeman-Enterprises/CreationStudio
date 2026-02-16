import gradio as gr
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

models = {}

def load_model(model_name):
    model_id = f"facebook/musicgen-{model_name}"
    if model_name not in models:
        print(f"Loading {model_id}...")
        proc = AutoProcessor.from_pretrained(model_id)
        # Keep on CPU — MPS has a channel limit bug with the audio decoder
        mod = MusicgenForConditionalGeneration.from_pretrained(model_id)
        models[model_name] = (proc, mod)
        print(f"{model_id} loaded!")
    return models[model_name]

print("Loading MusicGen Small for quick startup...")
load_model("small")

def generate_music(prompt, duration, model_size):
    processor, model = load_model(model_size)
    tokens = int(duration * 50)
    inputs = processor(text=[prompt], padding=True, return_tensors="pt")
    audio_values = model.generate(**inputs, max_new_tokens=tokens)
    audio = audio_values[0, 0].cpu().numpy()
    sample_rate = model.config.audio_encoder.sampling_rate
    return (sample_rate, audio)

demo = gr.Interface(
    fn=generate_music,
    inputs=[
        gr.Textbox(label="Describe the music", placeholder="e.g. epic orchestral trailer music with drums and brass"),
        gr.Slider(minimum=5, maximum=30, value=10, step=1, label="Duration (seconds)"),
        gr.Radio(
            choices=["small", "medium", "large"],
            value="small",
            label="Model Quality",
            info="Small=fast, Medium=balanced, Large=best quality (slower)"
        )
    ],
    outputs=gr.Audio(label="Generated Music"),
    title="MusicGen - AI Music Generator",
    description="Generate music from text. Small loads instantly. Medium/Large download on first use (~1-7GB)."
)

demo.launch(server_name="0.0.0.0", server_port=7860)
