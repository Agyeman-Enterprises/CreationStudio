# Creation Studio Manual

## Quick Start
Double-click **Creation Studio** on your Desktop or in Applications.
Pick Image, Music, or Video.

---

## IMAGE GEN (ComfyUI + SDXL)
**URL:** http://127.0.0.1:8188

### Your Models (in order of quality)
| Model | Best For | File |
|-------|----------|------|
| **Juggernaut XL v9** | Photorealistic images, portraits, landscapes | Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors |
| **SDXL Refiner** | Add detail pass after base generation | sd_xl_refiner_1.0.safetensors |
| **SDXL Base** | General purpose (decent but basic) | sd_xl_base_1.0.safetensors |

### How to Switch Models
1. Find the **Load Checkpoint** node in the workflow
2. Click the dropdown → pick your model
3. Hit **Queue Prompt**

### Best Settings for Quality
- **Resolution:** 1024x1024 (SDXL native), 1216x832 or 832x1216 for landscape/portrait
- **Steps:** 25-35 (more = better detail, slower)
- **CFG Scale:** 5-8 (lower = more creative, higher = stricter to prompt)
- **Sampler:** `euler` or `dpmpp_2m` with `karras` scheduler

### Prompting Tips
- Be specific: "a 35mm photograph of a woman in a red dress, golden hour lighting, shallow depth of field" > "woman in dress"
- Add quality tags: "masterpiece, best quality, highly detailed, 8k"
- Negative prompt matters: "ugly, deformed, blurry, low quality, watermark, text, jpeg artifacts"
- Style keywords: "cinematic", "concept art", "oil painting", "anime", "photorealistic"
- Lighting: "dramatic lighting", "soft lighting", "rim lighting", "volumetric fog"

### Using the Refiner (2-pass for better detail)
1. Generate with base/Juggernaut at 0.8 denoise
2. Connect output to a second KSampler with the Refiner model at 0.3 denoise
3. This adds fine detail to skin, textures, backgrounds

### Adding More Models
Download .safetensors files and drop them in:
`~/CreationStudio/ComfyUI/models/checkpoints/`

**Recommended downloads from civitai.com:**
- DreamShaper XL (versatile artistic)
- RealVisXL (photorealistic)
- Animagine XL (anime)

### Adding LoRAs (style/concept add-ons)
Drop .safetensors LoRA files in:
`~/CreationStudio/ComfyUI/models/loras/`
Then add a **LoRA Loader** node in your workflow.

### Adding ControlNet (pose/edge/depth control)
Drop ControlNet models in:
`~/CreationStudio/ComfyUI/models/controlnet/`
Lets you guide composition with reference images.

---

## MUSIC GEN
**URL:** http://127.0.0.1:7860

### How to Use
1. Type a description of the music you want
2. Set duration (5-30 seconds)
3. Click Submit

### Prompting Tips
- Genre + mood + instruments: "epic orchestral trailer music with drums and brass"
- Be specific about energy: "chill lo-fi hip hop beat with soft piano and vinyl crackle"
- Tempo: "fast-paced", "slow", "120 bpm"
- Reference styles: "80s synthwave", "jazz fusion", "ambient electronic"

### Good Prompts
- "upbeat electronic dance music with heavy bass and synth leads"
- "acoustic guitar folk song, warm and nostalgic, fingerpicking style"
- "dark cinematic orchestral music, tense and suspenseful, strings and percussion"
- "retro 8-bit chiptune game music, energetic and catchy"

---

## VIDEO GEN (Mochi)
**URL:** http://127.0.0.1:7861

### How to Use
1. Type a description of the video
2. Click Generate
3. First run downloads the model (~10GB)

### Tips
- Keep prompts simple and descriptive
- Short clips work best (2-4 seconds)
- Video gen is slow on CPU — be patient on M1 Max

---

## File Locations
| What | Where |
|------|-------|
| ComfyUI | ~/CreationStudio/ComfyUI/ |
| SDXL Models | ~/CreationStudio/ComfyUI/models/checkpoints/ |
| LoRAs | ~/CreationStudio/ComfyUI/models/loras/ |
| ControlNet | ~/CreationStudio/ComfyUI/models/controlnet/ |
| Generated Images | ~/CreationStudio/ComfyUI/output/ |
| MusicGen App | ~/CreationStudio/musicgen_app.py |
| Video Gen | ~/CreationStudio/mochi/ |

## Stopping Servers
Close the Terminal window that opened when you launched Creation Studio.

## Updating
```bash
cd ~/CreationStudio/ComfyUI && git pull
```

## Top Models to Download (2025-2026 tier list)
1. **Flux** (by Black Forest Labs) — current SOTA, needs separate setup
2. **Juggernaut XL v9** — best SDXL photorealism (you have this)
3. **DreamShaper XL** — best SDXL all-rounder
4. **RealVisXL V4** — photorealistic
5. **Animagine XL 3.1** — best anime
6. **SDXL Base + Refiner** — solid baseline (you have this)
