import torch

def detect_device():
    """Auto-detect best available device and dtype."""
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
        name = f"NVIDIA GPU ({torch.cuda.get_device_name(0)})"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
        dtype = torch.float32  # float16 causes black images on MPS
        name = "Apple Silicon GPU (MPS)"
    else:
        device = "cpu"
        dtype = torch.float32
        name = "CPU"
    print(f"[Device] Using {name} | dtype={dtype}")
    return device, dtype

DEVICE, DTYPE = detect_device()

# MusicGen always on CPU (MPS has channel limit bug >65536)
AUDIO_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
