# FILM frame-interpolation (+ optional upscale) i2v serverless worker for RunPod
# Base: RunPod's official ComfyUI serverless worker (ComfyUI + handler, no models).
#
# Nodes used are all BUILT INTO recent ComfyUI (no custom-node packs):
#   FrameInterpolationModelLoader, FrameInterpolate, BatchImagesNode,
#   CreateVideo, SaveVideo, UpscaleModelLoader, ImageUpscaleWithModel, ImageScale
#
# We bake in the FILM model (69 MB) + 3 ESRGAN upscalers so the request can pick
# any of them via `model_name`, with nothing downloaded at runtime.
FROM runpod/worker-comfyui:5.10.0-base

WORKDIR /comfyui

# --- Video encoding: give PyAV a real H.264 encoder (libx264) ---
# ComfyUI's SaveVideo encodes MP4/H.264 via the `av` (PyAV) library. The pip `av`
# wheel ships an LGPL ffmpeg WITHOUT libx264, so SaveVideo fails with:
#   avcodec_open2("libx264") -> Generic error in an external library
# Install a full ffmpeg (with libx264) + dev headers, then rebuild the SAME av
# version from source so it links against this ffmpeg and gains libx264.
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg \
      libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev \
      libavfilter-dev libswscale-dev libswresample-dev \
      pkg-config build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN AV_VER=$(/opt/venv/bin/pip show av | awk '/^Version:/{print $2}') && \
    /opt/venv/bin/pip install --force-reinstall --no-binary av "av==${AV_VER}"

RUN mkdir -p models/frame_interpolation models/upscale_models

# --- Frame interpolation model (FILM, 69 MB) -> models/frame_interpolation/ ---
RUN wget -O models/frame_interpolation/film_net_fp16.safetensors \
    "https://huggingface.co/Comfy-Org/frame_interpolation/resolve/main/frame_interpolation/film_net_fp16.safetensors"

# --- Upscale models (ESRGAN family) -> models/upscale_models/ ---
# 1) RealESRGAN x4plus  : general-purpose / photographic, 4x (~64 MB)
RUN wget -O models/upscale_models/RealESRGAN_x4plus.pth \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
# 2) 4x-UltraSharp      : sharper photoreal detail, 4x (~64 MB)
RUN wget -O models/upscale_models/4x-UltraSharp.pth \
    "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth"
# 3) RealESRGAN x4plus anime : anime / illustration / stylized, 4x (~18 MB)
RUN wget -O models/upscale_models/RealESRGAN_x4plus_anime_6B.pth \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
# 4) RealESRGAN x2plus  : general-purpose, native 2x = much faster for 2x targets (~64 MB)
RUN wget -O models/upscale_models/RealESRGAN_x2plus.pth \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth"

# The base image already sets the correct CMD to start ComfyUI + the RunPod handler.
