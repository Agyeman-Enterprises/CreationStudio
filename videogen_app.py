import gradio as gr
import torch
from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video

pipe = None

def load_pipeline():
    global pipe
    if pipe is None:
        print("Loading CogVideoX-2b (first run downloads ~10GB)...")
        pipe = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-2b",
            torch_dtype=torch.float16
        )
        pipe.enable_model_cpu_offload()
        print("CogVideoX ready!")
    return pipe

def generate_video(prompt, num_frames, guidance_scale):
    pipeline = load_pipeline()
    video = pipeline(
        prompt=prompt,
        num_videos_per_prompt=1,
        num_inference_steps=50,
        num_frames=num_frames,
        guidance_scale=guidance_scale,
    ).frames[0]

    output_path = "/tmp/cogvideo_output.mp4"
    export_to_video(video, output_path, fps=8)
    return output_path

demo = gr.Interface(
    fn=generate_video,
    inputs=[
        gr.Textbox(label="Describe your video", placeholder="e.g. A golden retriever running on a beach at sunset"),
        gr.Slider(minimum=8, maximum=48, value=16, step=8, label="Frames (more = longer video)"),
        gr.Slider(minimum=1, maximum=15, value=6, step=0.5, label="Guidance Scale"),
    ],
    outputs=gr.Video(label="Generated Video"),
    title="Video Gen - CogVideoX",
    description="Generate videos from text. First run downloads the model (~10GB). Generation takes a few minutes."
)

demo.launch(server_name="0.0.0.0", server_port=7861)
