import os
import datetime
import numpy as np
import torch
from .device import DEVICE

OUT_DIR = os.path.expanduser("~/CreationStudio/outputs/voice")

_model = None
_tokenizer = None

# Voice style descriptions for Parler TTS — plain English, not cryptic presets
VOICE_PRESETS = {
    "Female (Professional)": "A female speaker with a warm, professional voice delivers a clear narration at a moderate pace in a studio-quality recording.",
    "Female (Soft)": "A young woman speaks softly and gently, with a calm and soothing voice, in a quiet studio recording.",
    "Female (Energetic)": "A female speaker with an upbeat, energetic voice delivers an enthusiastic announcement with clear articulation.",
    "Male (Deep Narrator)": "A male speaker with a deep, resonant voice delivers a dramatic narration, speaking slowly and deliberately.",
    "Male (Conversational)": "A young man speaks casually and naturally, with a friendly conversational tone, in a close-mic studio recording.",
    "Male (Authoritative)": "A middle-aged man with a commanding, authoritative voice speaks clearly and confidently in a professional recording.",
    "Child (Bright)": "A child speaks with a bright, cheerful voice, pronouncing words clearly in a studio recording.",
    "Voiceover (Cinematic)": "A voice actor delivers a cinematic voiceover with dramatic pauses and emotional depth, in a high-quality studio recording.",
    "Voiceover (Commercial)": "A friendly, approachable voice delivers an advertising script with enthusiasm and clear diction in a professional studio.",
    "Game Character (Hero)": "A confident male voice actor delivers heroic game dialogue with bold expression and clear enunciation.",
}


def get_voice_names():
    return list(VOICE_PRESETS.keys())


def load_model():
    global _model, _tokenizer
    if _model is None:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        model_id = "parler-tts/parler-tts-mini-v1.1"
        print(f"[VoiceGen] Loading Parler TTS ({model_id})...")
        _tokenizer = AutoTokenizer.from_pretrained(model_id)
        _model = ParlerTTSForConditionalGeneration.from_pretrained(model_id).to(DEVICE)
        print(f"[VoiceGen] Parler TTS loaded on {DEVICE}")
    return _model, _tokenizer


def _split_sentences(text):
    """Split text into chunks for generation (Parler handles ~30s per chunk)."""
    import re
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    # Merge short fragments into chunks of ~150 chars
    chunks = []
    current = ""
    for part in parts:
        if len(current) + len(part) < 150:
            current = (current + " " + part).strip()
        else:
            if current:
                chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks if chunks else [text]


def generate_voice(text, voice_preset_name, export_fmt="WAV"):
    """Generate voice from text using Parler TTS. Returns (audio_tuple, file_path)."""
    model, tokenizer = load_model()
    description = VOICE_PRESETS.get(voice_preset_name, VOICE_PRESETS["Female (Professional)"])

    chunks = _split_sentences(text)
    all_audio = []
    sample_rate = model.config.sampling_rate

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        print(f"[VoiceGen] Generating segment {i+1}/{len(chunks)}: {chunk[:50]}...")

        input_ids = tokenizer(description, return_tensors="pt").input_ids.to(DEVICE)
        prompt_input_ids = tokenizer(chunk, return_tensors="pt").input_ids.to(DEVICE)

        with torch.no_grad():
            generation = model.generate(
                input_ids=input_ids,
                prompt_input_ids=prompt_input_ids,
            )

        audio_np = generation.cpu().numpy().squeeze()
        all_audio.append(audio_np)

        # Add brief silence between chunks
        if i < len(chunks) - 1:
            silence = np.zeros(int(sample_rate * 0.4))
            all_audio.append(silence)

    if not all_audio:
        return None, None

    full_audio = np.concatenate(all_audio)

    # Normalize audio
    max_val = np.max(np.abs(full_audio))
    if max_val > 0:
        full_audio = full_audio / max_val * 0.95

    # Save
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    import scipy.io.wavfile
    audio_int16 = np.clip(full_audio * 32767, -32768, 32767).astype(np.int16)
    wav_path = os.path.join(OUT_DIR, f"voice_{ts}.wav")
    scipy.io.wavfile.write(wav_path, sample_rate, audio_int16)

    export_fmt = export_fmt.lower()
    if export_fmt == "wav":
        return (sample_rate, full_audio), wav_path

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
        return (sample_rate, full_audio), out_path
    except ImportError:
        print("[VoiceGen] pydub not available, returning WAV")
        return (sample_rate, full_audio), wav_path
