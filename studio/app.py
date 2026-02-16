"""
Creation Studio - Unified AI Creation Suite
A Leonardo.ai-style app for image, music, and video generation.
"""

import gradio as gr
import os

# Import modules
from . import image_gen, image_tools, logo_export, audio_lab, video_gen, gallery

CUSTOM_CSS = """
/* Dark theme overrides */
:root {
    --body-background-fill: #0a0a0f !important;
    --background-fill-primary: #12121a !important;
    --background-fill-secondary: #1a1a2e !important;
    --block-background-fill: #16161f !important;
    --block-border-color: #2a2a3e !important;
    --border-color-primary: #2a2a3e !important;
    --color-accent: #7c3aed !important;
    --color-accent-soft: #7c3aed33 !important;
    --body-text-color: #e0e0e8 !important;
    --body-text-color-subdued: #8888aa !important;
    --input-background-fill: #1e1e2e !important;
}

.gradio-container {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%) !important;
    max-width: 1400px !important;
    font-size: 16px !important;
}

/* Header */
.studio-header {
    text-align: center;
    padding: 20px 0;
    background: linear-gradient(135deg, #7c3aed22, #2563eb22);
    border-radius: 12px;
    margin-bottom: 16px;
}
.studio-header h1 {
    font-size: 2.5em !important;
    background: linear-gradient(135deg, #7c3aed, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 !important;
}
.studio-header p {
    color: #8888aa !important;
    font-size: 1.1em !important;
}

/* Tabs */
.tabs > .tab-nav {
    background: #12121a !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.tabs > .tab-nav > button {
    background: transparent !important;
    color: #8888aa !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.tabs > .tab-nav > button.selected {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
}
.tabs > .tab-nav > button:hover:not(.selected) {
    background: #1e1e2e !important;
    color: #e0e0e8 !important;
}

/* Buttons */
.primary {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 12px 32px !important;
    border-radius: 10px !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 15px #7c3aed44 !important;
}
.primary:hover {
    box-shadow: 0 6px 25px #7c3aed66 !important;
    transform: translateY(-1px) !important;
}
.secondary {
    background: #1e1e2e !important;
    border: 1px solid #7c3aed44 !important;
    color: #c0c0d0 !important;
    border-radius: 8px !important;
}

/* Inputs */
textarea, input[type="text"], input[type="number"] {
    background: #1e1e2e !important;
    border: 1px solid #2a2a3e !important;
    color: #e0e0e8 !important;
    border-radius: 8px !important;
    font-size: 15px !important;
}
textarea:focus, input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 10px #7c3aed33 !important;
}

/* Sliders */
input[type="range"] {
    accent-color: #7c3aed !important;
}

/* Cards / blocks */
.block {
    background: #16161f !important;
    border: 1px solid #2a2a3e !important;
    border-radius: 12px !important;
}

/* Image output */
.image-container {
    border-radius: 12px !important;
    overflow: hidden;
}

/* Gallery */
.gallery-item {
    border-radius: 8px !important;
    border: 2px solid transparent !important;
    transition: border-color 0.2s !important;
}
.gallery-item:hover {
    border-color: #7c3aed !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }

/* Labels */
label { font-size: 14px !important; font-weight: 600 !important; color: #c0c0d0 !important; }
"""


def build_app():
    with gr.Blocks(
        title="Creation Studio",
        css=CUSTOM_CSS,
        theme=gr.themes.Base(),
    ) as app:

        # Header
        gr.HTML("""
        <div class="studio-header">
            <h1>Creation Studio</h1>
            <p>AI-Powered Image, Music & Video Generation</p>
        </div>
        """)

        with gr.Tabs():

            # ============ IMAGE GEN TAB ============
            with gr.Tab("Image Gen", id="imagegen"):
                with gr.Row():
                    with gr.Column(scale=1):
                        img_prompt = gr.Textbox(
                            label="Prompt",
                            lines=3,
                            placeholder="a cinematic photo of a mountain lake at sunrise, golden light, mist rising, 8k",
                        )
                        img_negative = gr.Textbox(
                            label="Negative Prompt",
                            value="ugly, deformed, blurry, low quality, watermark, text, jpeg artifacts",
                        )
                        img_model = gr.Dropdown(
                            choices=image_gen.get_models(),
                            value=image_gen.get_default_model(),
                            label="Model",
                        )
                        with gr.Row():
                            img_width = gr.Slider(512, 1536, 1024, step=64, label="Width")
                            img_height = gr.Slider(512, 1536, 1024, step=64, label="Height")
                        with gr.Row():
                            img_steps = gr.Slider(10, 50, 25, step=1, label="Steps")
                            img_cfg = gr.Slider(1, 15, 7, step=0.5, label="CFG Scale")
                        img_seed = gr.Number(label="Seed (0 = random)", value=0)

                        with gr.Row():
                            img_export_fmt = gr.Dropdown(
                                choices=["PNG", "JPG", "SVG", "PDF"],
                                value="PNG",
                                label="Export Format",
                            )

                        with gr.Row():
                            img_gen_btn = gr.Button("Generate", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        img_output = gr.Image(label="Result", type="pil")
                        with gr.Row():
                            img_upscale_btn = gr.Button("Upscale 4x", variant="secondary")
                            img_rmbg_btn = gr.Button("Remove BG", variant="secondary")
                            img_export_btn = gr.Button("Export", variant="secondary")
                            img_logo_btn = gr.Button("Logo Pack (ZIP)", variant="secondary")
                        img_file_output = gr.File(label="Download", visible=True)

                # Image Gen events
                img_gen_btn.click(
                    fn=image_gen.generate,
                    inputs=[img_prompt, img_negative, img_model, img_width, img_height, img_steps, img_cfg, img_seed],
                    outputs=img_output,
                )
                img_upscale_btn.click(
                    fn=image_tools.upscale_image,
                    inputs=[img_output],
                    outputs=img_output,
                )
                img_rmbg_btn.click(
                    fn=image_tools.remove_background,
                    inputs=[img_output],
                    outputs=img_output,
                )
                img_export_btn.click(
                    fn=logo_export.export_image,
                    inputs=[img_output, img_export_fmt],
                    outputs=img_file_output,
                )
                img_logo_btn.click(
                    fn=logo_export.export_logo_pack,
                    inputs=[img_output],
                    outputs=img_file_output,
                )

            # ============ IMAGE TOOLS TAB ============
            with gr.Tab("Image Tools", id="imagetools"):
                with gr.Tabs():

                    # Upscale sub-tab
                    with gr.Tab("Upscale"):
                        with gr.Row():
                            with gr.Column():
                                tool_up_input = gr.Image(label="Input Image", type="pil")
                                tool_up_scale = gr.Slider(2, 4, 4, step=1, label="Scale Factor")
                                tool_up_btn = gr.Button("Upscale", variant="primary")
                            with gr.Column():
                                tool_up_output = gr.Image(label="Upscaled", type="pil")
                        tool_up_btn.click(
                            fn=image_tools.upscale_image,
                            inputs=[tool_up_input, tool_up_scale],
                            outputs=tool_up_output,
                        )

                    # Remove BG sub-tab
                    with gr.Tab("Remove Background"):
                        with gr.Row():
                            with gr.Column():
                                tool_bg_input = gr.Image(label="Input Image", type="pil")
                                tool_bg_btn = gr.Button("Remove Background", variant="primary")
                            with gr.Column():
                                tool_bg_output = gr.Image(label="Result (Transparent)", type="pil")
                        tool_bg_btn.click(
                            fn=image_tools.remove_background,
                            inputs=[tool_bg_input],
                            outputs=tool_bg_output,
                        )

                    # Img2Img sub-tab
                    with gr.Tab("Img2Img"):
                        with gr.Row():
                            with gr.Column():
                                tool_i2i_input = gr.Image(label="Input Image", type="pil")
                                tool_i2i_prompt = gr.Textbox(label="Prompt", placeholder="Transform into oil painting style")
                                tool_i2i_neg = gr.Textbox(label="Negative Prompt", value="ugly, deformed, blurry")
                                tool_i2i_model = gr.Dropdown(
                                    choices=image_gen.get_models(),
                                    value=image_gen.get_default_model(),
                                    label="Model",
                                )
                                tool_i2i_denoise = gr.Slider(0.1, 1.0, 0.6, step=0.05, label="Denoise Strength")
                                tool_i2i_steps = gr.Slider(10, 50, 25, step=1, label="Steps")
                                tool_i2i_cfg = gr.Slider(1, 15, 7, step=0.5, label="CFG Scale")
                                tool_i2i_btn = gr.Button("Transform", variant="primary")
                            with gr.Column():
                                tool_i2i_output = gr.Image(label="Result", type="pil")
                        tool_i2i_btn.click(
                            fn=image_tools.img2img,
                            inputs=[tool_i2i_input, tool_i2i_prompt, tool_i2i_neg, tool_i2i_model, tool_i2i_denoise, tool_i2i_steps, tool_i2i_cfg],
                            outputs=tool_i2i_output,
                        )

                    # Stitch & Tile sub-tab
                    with gr.Tab("Stitch & Tile"):
                        gr.Markdown("### Sprite Sheet Maker")
                        with gr.Row():
                            with gr.Column():
                                tool_st_input = gr.File(label="Upload Images", file_count="multiple", file_types=["image"])
                                tool_st_cols = gr.Slider(1, 10, 4, step=1, label="Columns")
                                tool_st_padding = gr.Slider(0, 32, 0, step=2, label="Padding (px)")
                                tool_st_btn = gr.Button("Create Sprite Sheet", variant="primary")
                            with gr.Column():
                                tool_st_output = gr.Image(label="Sprite Sheet", type="pil")

                        def _stitch_from_files(files, cols, padding):
                            if not files:
                                return None
                            from PIL import Image as PILImage
                            images = [PILImage.open(f.name) for f in files]
                            return image_tools.stitch_sprite_sheet(images, cols, int(padding))

                        tool_st_btn.click(
                            fn=_stitch_from_files,
                            inputs=[tool_st_input, tool_st_cols, tool_st_padding],
                            outputs=tool_st_output,
                        )

                        gr.Markdown("---\n### Seamless Tile Maker")
                        with gr.Row():
                            with gr.Column():
                                tool_tile_input = gr.Image(label="Input Image", type="pil")
                                tool_tile_btn = gr.Button("Make Seamless Tile", variant="primary")
                            with gr.Column():
                                tool_tile_output = gr.Image(label="Tileable Result", type="pil")
                        tool_tile_btn.click(
                            fn=image_tools.make_seamless_tile,
                            inputs=[tool_tile_input],
                            outputs=tool_tile_output,
                        )

            # ============ AUDIO LAB TAB ============
            with gr.Tab("Audio Lab", id="audiolab"):
                with gr.Tabs():

                    # Single generation
                    with gr.Tab("Generate"):
                        with gr.Row():
                            with gr.Column(scale=1):
                                aud_category = gr.Radio(
                                    choices=["BGM", "SFX", "Ambient"],
                                    value="BGM",
                                    label="Category",
                                )
                                aud_prompt = gr.Textbox(
                                    label="Describe the audio",
                                    lines=2,
                                    placeholder="epic orchestral trailer music with drums and brass",
                                )
                                aud_duration = gr.Slider(1, 30, 15, step=1, label="Duration (seconds)")
                                aud_model = gr.Radio(
                                    choices=["small", "medium", "large"],
                                    value="small",
                                    label="Model Quality",
                                    info="Small=fast, Medium=balanced, Large=best (slower)",
                                )
                                aud_loop = gr.Checkbox(label="Make Loopable", value=False)
                                aud_format = gr.Radio(
                                    choices=["WAV", "MP3", "OGG"],
                                    value="WAV",
                                    label="Export Format",
                                )
                                aud_gen_btn = gr.Button("Generate", variant="primary", size="lg")

                            with gr.Column(scale=1):
                                aud_output = gr.Audio(label="Generated Audio")
                                aud_file = gr.File(label="Download")

                        # Update placeholder and duration based on category
                        def update_category(cat):
                            preset = audio_lab.CATEGORY_PRESETS.get(cat, {})
                            dur_min, dur_max = preset.get("duration_range", (1, 30))
                            default_dur = preset.get("default_duration", 10)
                            placeholder = preset.get("placeholder", "")
                            return (
                                gr.update(placeholder=placeholder),
                                gr.update(minimum=dur_min, maximum=dur_max, value=default_dur),
                            )

                        aud_category.change(
                            fn=update_category,
                            inputs=[aud_category],
                            outputs=[aud_prompt, aud_duration],
                        )

                        def _generate_audio(prompt, duration, model, category, loop, fmt):
                            audio_tuple, path = audio_lab.generate_and_process(
                                prompt, duration, model, category, loop, fmt
                            )
                            return audio_tuple, path

                        aud_gen_btn.click(
                            fn=_generate_audio,
                            inputs=[aud_prompt, aud_duration, aud_model, aud_category, aud_loop, aud_format],
                            outputs=[aud_output, aud_file],
                        )

                    # Chain / Stitch
                    with gr.Tab("Chain / Stitch"):
                        gr.Markdown("Generate multiple audio segments and stitch them into one track.\nPut each prompt on a new line.")
                        with gr.Row():
                            with gr.Column(scale=1):
                                chain_prompts = gr.Textbox(
                                    label="Prompts (one per line)",
                                    lines=6,
                                    placeholder="calm ambient intro with soft pads\nintense battle drums and brass\nvictory fanfare with orchestra",
                                )
                                chain_dur = gr.Slider(3, 15, 8, step=1, label="Duration per segment (sec)")
                                chain_model = gr.Radio(
                                    choices=["small", "medium", "large"],
                                    value="small",
                                    label="Model Quality",
                                )
                                chain_crossfade = gr.Slider(0, 2000, 500, step=100, label="Crossfade (ms)")
                                chain_format = gr.Radio(choices=["WAV", "MP3", "OGG"], value="WAV", label="Format")
                                chain_btn = gr.Button("Generate Chain", variant="primary", size="lg")

                            with gr.Column(scale=1):
                                chain_output = gr.Audio(label="Stitched Audio")
                                chain_file = gr.File(label="Download")

                        chain_btn.click(
                            fn=audio_lab.generate_chain,
                            inputs=[chain_prompts, chain_dur, chain_model, chain_crossfade, chain_format],
                            outputs=[chain_output, chain_file],
                        )

            # ============ VIDEO GEN TAB ============
            with gr.Tab("Video Gen", id="videogen"):
                with gr.Row():
                    with gr.Column(scale=1):
                        vid_prompt = gr.Textbox(
                            label="Describe your video",
                            lines=2,
                            placeholder="A golden retriever running on a beach at sunset",
                        )
                        vid_frames = gr.Slider(8, 48, 16, step=8, label="Frames (more = longer video)")
                        vid_guidance = gr.Slider(1, 15, 6, step=0.5, label="Guidance Scale")
                        vid_fps = gr.Dropdown(
                            choices=["8", "15", "24", "30"],
                            value="8",
                            label="FPS",
                        )
                        vid_preset = gr.Dropdown(
                            choices=list(video_gen.SOCIAL_PRESETS.keys()),
                            value="YouTube / Twitter (16:9)",
                            label="Social Media Preset",
                        )
                        with gr.Row(visible=False) as vid_custom_row:
                            vid_custom_w = gr.Number(label="Custom Width", value=1920)
                            vid_custom_h = gr.Number(label="Custom Height", value=1080)
                        vid_format = gr.Dropdown(
                            choices=["MP4", "GIF", "WebM"],
                            value="MP4",
                            label="Output Format",
                        )
                        vid_gen_btn = gr.Button("Generate", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        vid_output = gr.Video(label="Generated Video")
                        vid_file = gr.File(label="Download")

                # Show/hide custom dimensions
                def toggle_custom(preset):
                    return gr.update(visible=(preset == "Custom"))

                vid_preset.change(fn=toggle_custom, inputs=[vid_preset], outputs=[vid_custom_row])

                def _gen_video(prompt, frames, guidance, fps, preset, fmt, cw, ch):
                    path = video_gen.generate_video(prompt, frames, guidance, int(fps), preset, fmt.lower(), cw, ch)
                    return path, path

                vid_gen_btn.click(
                    fn=_gen_video,
                    inputs=[vid_prompt, vid_frames, vid_guidance, vid_fps, vid_preset, vid_format, vid_custom_w, vid_custom_h],
                    outputs=[vid_output, vid_file],
                )

            # ============ GALLERY TAB ============
            with gr.Tab("Gallery", id="gallery"):
                with gr.Row():
                    gal_refresh = gr.Button("Refresh Gallery", variant="secondary")

                gr.Markdown("### Images")
                gal_images = gr.Gallery(label="Generated Images", columns=4, height="auto")

                gr.Markdown("### Audio")
                gal_audio_list = gr.Dataframe(
                    headers=["File", "Type", "Size"],
                    label="Audio Files",
                )

                gr.Markdown("### Video")
                gal_video_list = gr.Dataframe(
                    headers=["File", "Format", "Size"],
                    label="Video Files",
                )

                def refresh_gallery():
                    images = gallery.get_image_gallery()
                    audio_files = gallery.get_audio_files()
                    video_files = gallery.get_video_files()

                    audio_data = []
                    for f in audio_files:
                        name = os.path.basename(f)
                        ext = os.path.splitext(f)[1]
                        size = f"{os.path.getsize(f) / 1024:.0f} KB"
                        audio_data.append([name, ext, size])

                    video_data = []
                    for f in video_files:
                        name = os.path.basename(f)
                        ext = os.path.splitext(f)[1]
                        size = f"{os.path.getsize(f) / (1024*1024):.1f} MB"
                        video_data.append([name, ext, size])

                    return images, audio_data, video_data

                gal_refresh.click(
                    fn=refresh_gallery,
                    outputs=[gal_images, gal_audio_list, gal_video_list],
                )

                # Auto-load on tab visit
                app.load(fn=refresh_gallery, outputs=[gal_images, gal_audio_list, gal_video_list])

    return app


def launch():
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)


if __name__ == "__main__":
    launch()
