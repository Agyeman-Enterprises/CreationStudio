import os
import io
import datetime
import numpy as np
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from .device import AUDIO_DEVICE

OUT_DIR = os.path.expanduser("~/CreationStudio/outputs/audio")

_models = {}

CATEGORY_PRESETS = {
    "BGM": {
        "placeholder": "epic orchestral trailer music with drums and brass",
        "duration_range": (10, 30),
        "default_duration": 15,
    },
    "SFX": {
        "placeholder": "explosion sound effect, cinematic boom",
        "duration_range": (1, 8),
        "default_duration": 3,
    },
    "Ambient": {
        "placeholder": "rain on a tin roof, gentle thunder in the distance",
        "duration_range": (10, 30),
        "default_duration": 20,
    },
}


def load_model(model_size="small"):
    """Load MusicGen model (small/medium/large)."""
    if model_size not in _models:
        model_id = f"facebook/musicgen-{model_size}"
        print(f"[AudioLab] Loading {model_id}...")
        proc = AutoProcessor.from_pretrained(model_id)
        mod = MusicgenForConditionalGeneration.from_pretrained(model_id)
        mod = mod.to(AUDIO_DEVICE)
        _models[model_size] = (proc, mod)
        print(f"[AudioLab] {model_id} loaded on {AUDIO_DEVICE}")
    return _models[model_size]


def generate_audio(prompt, duration, model_size="small"):
    """Generate audio from text prompt. Returns (sample_rate, numpy_array)."""
    processor, model = load_model(model_size)
    tokens = int(duration * 50)
    inputs = processor(text=[prompt], padding=True, return_tensors="pt")
    inputs = {k: v.to(AUDIO_DEVICE) for k, v in inputs.items()}
    audio_values = model.generate(**inputs, max_new_tokens=tokens)
    audio = audio_values[0, 0].cpu().numpy()
    sample_rate = model.config.audio_encoder.sampling_rate
    return sample_rate, audio


def make_loopable(audio, sample_rate, crossfade_ms=500):
    """Crossfade start and end for seamless looping."""
    crossfade_samples = int(sample_rate * crossfade_ms / 1000)
    if len(audio) < crossfade_samples * 2:
        return audio

    result = audio.copy()
    fade_in = np.linspace(0, 1, crossfade_samples)
    fade_out = np.linspace(1, 0, crossfade_samples)

    # Blend end into start
    end_segment = audio[-crossfade_samples:] * fade_out
    start_segment = audio[:crossfade_samples] * fade_in
    result[:crossfade_samples] = start_segment + end_segment
    result[-crossfade_samples:] = result[:crossfade_samples]  # mirror

    return result


def stitch_segments(segments, sample_rate, crossfade_ms=200):
    """Stitch multiple audio segments with crossfade."""
    if len(segments) == 0:
        return np.array([])
    if len(segments) == 1:
        return segments[0]

    crossfade_samples = int(sample_rate * crossfade_ms / 1000)
    result = segments[0]

    for seg in segments[1:]:
        if crossfade_samples > 0 and len(result) >= crossfade_samples and len(seg) >= crossfade_samples:
            fade_out = np.linspace(1, 0, crossfade_samples)
            fade_in = np.linspace(0, 1, crossfade_samples)
            overlap = result[-crossfade_samples:] * fade_out + seg[:crossfade_samples] * fade_in
            result = np.concatenate([result[:-crossfade_samples], overlap, seg[crossfade_samples:]])
        else:
            result = np.concatenate([result, seg])

    return result


def generate_and_process(prompt, duration, model_size, category, loop, export_fmt):
    """Full pipeline: generate + optional loop + save in chosen format."""
    sample_rate, audio = generate_audio(prompt, duration, model_size)

    if loop:
        audio = make_loopable(audio, sample_rate)

    # Save
    cat_dir = os.path.join(OUT_DIR, category.lower())
    os.makedirs(cat_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    export_fmt = export_fmt.lower()
    wav_path = os.path.join(cat_dir, f"{category.lower()}_{ts}.wav")

    # Always save WAV first
    import scipy.io.wavfile
    audio_int16 = (audio * 32767).astype(np.int16)
    scipy.io.wavfile.write(wav_path, sample_rate, audio_int16)

    if export_fmt == "wav":
        return (sample_rate, audio), wav_path

    # Convert using pydub if available
    try:
        from pydub import AudioSegment
        sound = AudioSegment.from_wav(wav_path)
        if export_fmt == "mp3":
            out_path = wav_path.replace(".wav", ".mp3")
            sound.export(out_path, format="mp3")
        elif export_fmt == "ogg":
            out_path = wav_path.replace(".wav", ".ogg")
            sound.export(out_path, format="ogg")
        else:
            out_path = wav_path
        return (sample_rate, audio), out_path
    except ImportError:
        print("[AudioLab] pydub not available, returning WAV")
        return (sample_rate, audio), wav_path


def generate_chain(prompts_text, duration_each, model_size, crossfade_ms, export_fmt):
    """Generate multiple segments from newline-separated prompts, stitch them."""
    prompts = [p.strip() for p in prompts_text.strip().split("\n") if p.strip()]
    if not prompts:
        return None, None

    segments = []
    sample_rate = None
    for i, prompt in enumerate(prompts):
        print(f"[AudioLab] Generating segment {i+1}/{len(prompts)}: {prompt[:50]}...")
        sr, audio = generate_audio(prompt, duration_each, model_size)
        segments.append(audio)
        sample_rate = sr

    stitched = stitch_segments(segments, sample_rate, crossfade_ms)

    cat_dir = os.path.join(OUT_DIR, "bgm")
    os.makedirs(cat_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    import scipy.io.wavfile
    audio_int16 = (stitched * 32767).astype(np.int16)
    wav_path = os.path.join(cat_dir, f"chain_{ts}.wav")
    scipy.io.wavfile.write(wav_path, sample_rate, audio_int16)

    return (sample_rate, stitched), wav_path
