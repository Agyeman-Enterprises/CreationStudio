"""
Creation Studio - Unified AI Creation Suite
A Leonardo.ai-style app for image, music, video, and voice generation.
"""

import gradio as gr
import os

# Import modules
from . import image_gen, image_tools, logo_export, audio_lab, video_gen, voice_gen, gallery

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
    --body-text-color-subdued: #b0b0c8 !important;
    --input-background-fill: #1e1e2e !important;
    --button-primary-text-color: #ffffff !important;
    --button-secondary-text-color: #e0e0e8 !important;
    --checkbox-label-text-color: #e0e0e8 !important;
}

/* Force all text white/light on dark backgrounds */
.gradio-container, .gradio-container * {
    color: #e0e0e8;
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
    color: #b0b0c8 !important;
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
    color: #b0b0c8 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.tabs > .tab-nav > button.selected {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: #ffffff !important;
}
.tabs > .tab-nav > button:hover:not(.selected) {
    background: #1e1e2e !important;
    color: #e0e0e8 !important;
}

/* Buttons */
.primary, button.primary {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 12px 32px !important;
    border-radius: 10px !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 15px #7c3aed44 !important;
    color: #ffffff !important;
}
.primary:hover, button.primary:hover {
    box-shadow: 0 6px 25px #7c3aed66 !important;
    transform: translateY(-1px) !important;
    color: #ffffff !important;
}
.secondary, button.secondary {
    background: #1e1e2e !important;
    border: 1px solid #7c3aed44 !important;
    color: #e0e0e8 !important;
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
textarea::placeholder, input::placeholder {
    color: #6a6a8a !important;
}

/* Dropdowns */
select, .wrap option, [data-testid="dropdown"] {
    background: #1e1e2e !important;
    color: #e0e0e8 !important;
}

/* Radio / Checkbox labels */
.wrap label span, .radio-group label, .checkbox-group label,
input[type="radio"] + label, input[type="checkbox"] + label,
.gr-radio label, .gr-checkbox label {
    color: #e0e0e8 !important;
}

/* Sliders */
input[type="range"] {
    accent-color: #7c3aed !important;
}
.range-slider .label, .range-slider span {
    color: #e0e0e8 !important;
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

/* Markdown text */
.prose, .prose *, .markdown-text, .markdown-text * {
    color: #e0e0e8 !important;
}
.prose h1, .prose h2, .prose h3, .prose h4 {
    color: #ffffff !important;
}

/* Dataframe / table */
table, th, td {
    color: #e0e0e8 !important;
    border-color: #2a2a3e !important;
}
th {
    background: #1a1a2e !important;
    color: #c0c0d8 !important;
}
td {
    background: #16161f !important;
}

/* File upload / download */
.file-preview, .upload-text {
    color: #e0e0e8 !important;
}

/* Info text */
.info-text, .gr-form .info, span.info {
    color: #9898b8 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }

/* Labels */
label, label span {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #c0c0d8 !important;
}

/* Dropdown fix - force dark bg on all dropdown internals */
.gradio-dropdown .wrap,
.gradio-dropdown .wrap-inner,
.gradio-dropdown .secondary-wrap,
.gradio-dropdown .single-select,
.gradio-dropdown input,
.gradio-dropdown .options,
.gradio-dropdown ul,
.gradio-dropdown li,
.gradio-dropdown .token,
[data-testid="dropdown"],
[data-testid="dropdown"] .wrap,
[data-testid="dropdown"] input,
[data-testid="dropdown"] .single-select,
.svelte-dropdown,
div[role="listbox"],
div[role="option"] {
    background: #1e1e2e !important;
    background-color: #1e1e2e !important;
    color: #e0e0e8 !important;
}
.gradio-dropdown ul.options,
div[role="listbox"] {
    background: #16161f !important;
    border: 1px solid #2a2a3e !important;
}
.gradio-dropdown ul.options li:hover,
.gradio-dropdown ul.options li.active,
.gradio-dropdown ul.options li.selected,
div[role="option"]:hover,
div[role="option"][aria-selected="true"] {
    background: #7c3aed !important;
    color: #ffffff !important;
}

/* Force all buttons to have visible text */
button {
    color: #e0e0e8 !important;
}
button.primary, .primary button {
    color: #ffffff !important;
}
"""

PWA_HEAD = """
<meta name="theme-color" content="#7c3aed">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Creation Studio">
<link rel="apple-touch-icon" href="/pwa/icon-192.png">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(r => console.log('[PWA] Service worker registered, scope:', r.scope))
      .catch(e => console.warn('[PWA] SW registration failed:', e));
  });
}
</script>
"""


def build_app():
    with gr.Blocks(
        title="Creation Studio",
    ) as app:

        # Header
        gr.HTML("""
        <div class="studio-header">
            <h1>Creation Studio</h1>
            <p>AI-Powered Image, Music, Video & Voice Generation</p>
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

            # ============ VOICE GEN TAB ============
            with gr.Tab("Voice Gen", id="voicegen"):
                gr.Markdown("### AI Voice Generation\nGenerate voiceovers, narration, and character voices. Powered by Parler TTS.")
                with gr.Row():
                    with gr.Column(scale=1):
                        vox_text = gr.Textbox(
                            label="Text to speak",
                            lines=6,
                            placeholder="Welcome to Creation Studio. This is your all-in-one creative suite for images, music, video, and voice.",
                        )
                        vox_voice = gr.Dropdown(
                            choices=voice_gen.get_voice_names(),
                            value=voice_gen.get_voice_names()[0],
                            label="Voice Preset",
                        )
                        vox_format = gr.Radio(
                            choices=["WAV", "MP3", "OGG"],
                            value="WAV",
                            label="Export Format",
                        )
                        vox_gen_btn = gr.Button("Generate Voice", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        vox_output = gr.Audio(label="Generated Voice")
                        vox_file = gr.File(label="Download")

                def _generate_voice(text, voice_name, fmt):
                    audio_tuple, path = voice_gen.generate_voice(text, voice_name, fmt)
                    return audio_tuple, path

                vox_gen_btn.click(
                    fn=_generate_voice,
                    inputs=[vox_text, vox_voice, vox_format],
                    outputs=[vox_output, vox_file],
                )

            # ============ VIDEO GEN TAB ============
            with gr.Tab("Video Gen", id="videogen"):
                with gr.Tabs():

                    # Single clip
                    with gr.Tab("Single Clip"):
                        with gr.Row():
                            with gr.Column(scale=1):
                                vid_prompt = gr.Textbox(
                                    label="Describe your video",
                                    lines=2,
                                    placeholder="A golden retriever running on a beach at sunset, cinematic lighting",
                                )
                                vid_frames = gr.Slider(16, 81, 33, step=8, label="Frames (more = longer clip)")
                                vid_guidance = gr.Slider(1, 15, 5, step=0.5, label="Guidance Scale")
                                vid_fps = gr.Dropdown(
                                    choices=["8", "15", "24", "30"],
                                    value="15",
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

                    # Video Chain
                    with gr.Tab("Video Chain"):
                        gr.Markdown("### Multi-Clip Video\nGenerate multiple clips from separate prompts and stitch them into one video.\nPut each scene description on a new line.")
                        with gr.Row():
                            with gr.Column(scale=1):
                                vchain_prompts = gr.Textbox(
                                    label="Scene prompts (one per line)",
                                    lines=8,
                                    placeholder="Wide establishing shot of a futuristic city at dawn, aerial view\nClose-up of a woman walking through neon-lit streets, cinematic\nSlow motion shot of rain falling on glass windows, reflections\nDrone shot pulling away from the city skyline at sunset",
                                )
                                vchain_frames = gr.Slider(16, 81, 33, step=8, label="Frames per clip")
                                vchain_guidance = gr.Slider(1, 15, 5, step=0.5, label="Guidance Scale")
                                vchain_fps = gr.Dropdown(
                                    choices=["8", "15", "24", "30"],
                                    value="15",
                                    label="FPS",
                                )
                                vchain_crossfade = gr.Slider(0, 30, 8, step=1, label="Crossfade (frames)")
                                vchain_preset = gr.Dropdown(
                                    choices=list(video_gen.SOCIAL_PRESETS.keys()),
                                    value="YouTube / Twitter (16:9)",
                                    label="Social Media Preset",
                                )
                                with gr.Row(visible=False) as vchain_custom_row:
                                    vchain_custom_w = gr.Number(label="Custom Width", value=1920)
                                    vchain_custom_h = gr.Number(label="Custom Height", value=1080)
                                vchain_format = gr.Dropdown(
                                    choices=["MP4", "GIF", "WebM"],
                                    value="MP4",
                                    label="Output Format",
                                )
                                vchain_btn = gr.Button("Generate Video Chain", variant="primary", size="lg")

                            with gr.Column(scale=1):
                                vchain_output = gr.Video(label="Stitched Video")
                                vchain_file = gr.File(label="Download")

                        vchain_preset.change(
                            fn=toggle_custom,
                            inputs=[vchain_preset],
                            outputs=[vchain_custom_row],
                        )

                        def _gen_video_chain(prompts, frames, guidance, fps, preset, fmt, crossfade, cw, ch):
                            path = video_gen.generate_video_chain(
                                prompts, frames, guidance, int(fps), preset, fmt.lower(), crossfade, cw, ch
                            )
                            return path, path

                        vchain_btn.click(
                            fn=_gen_video_chain,
                            inputs=[vchain_prompts, vchain_frames, vchain_guidance, vchain_fps, vchain_preset, vchain_format, vchain_crossfade, vchain_custom_w, vchain_custom_h],
                            outputs=[vchain_output, vchain_file],
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
    import os
    import socket
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    outputs_dir = os.path.expanduser("~/CreationStudio/outputs")
    models_dir = os.path.expanduser("~/CreationStudio/ComfyUI/models")
    studio_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pwa_dir = os.path.join(studio_root, "pwa")
    icon_path = os.path.join(pwa_dir, "icon-512.png")

    gradio_app = build_app()

    # FastAPI wrapper: serves PWA static files + Gradio app
    from fastapi.responses import FileResponse

    fastapi_app = FastAPI()
    fastapi_app.mount("/pwa", StaticFiles(directory=pwa_dir), name="pwa")

    @fastapi_app.get("/sw.js")
    async def service_worker():
        return FileResponse(
            os.path.join(pwa_dir, "sw.js"),
            media_type="application/javascript",
        )

    gr.mount_gradio_app(
        fastapi_app,
        gradio_app,
        path="/",
        pwa=True,
        favicon_path=icon_path,
        allowed_paths=[outputs_dir, models_dir],
        css=CUSTOM_CSS,
        theme=gr.themes.Base(),
        head=PWA_HEAD,
    )

    # Print launch info
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    print(f"\n  {'='*50}")
    print(f"  Creation Studio")
    print(f"  {'='*50}")
    print(f"  Local:   http://127.0.0.1:7860")
    print(f"  Network: http://{local_ip}:7860")
    print(f"  PWA:     Install via browser menu on any device")
    print(f"  {'='*50}\n")

    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    launch()
