# HunyuanVideo 1.5 i2v serverless worker for RunPod
# Base: RunPod's official ComfyUI serverless worker (ComfyUI + handler, no models)
# We bake in the 5 models so workers never download from Hugging Face at runtime.
FROM runpod/worker-comfyui:5.10.0-base

# aria2 = multi-connection downloader. Pulls the ~19.5 GB of weights fast enough
# to finish inside RunPod's 30-minute build limit (plain wget was too slow).
RUN apt-get update && apt-get install -y aria2 && rm -rf /var/lib/apt/lists/*

# ComfyUI lives at /comfyui in this base image.
WORKDIR /comfyui
RUN mkdir -p models/diffusion_models models/text_encoders models/vae models/clip_vision

# -x16 -s16 = 16 parallel connections per file. Downloads happen ONCE, at build time.
# --- Diffusion model (UNet): 480p i2v step-distilled, fp8 (8.34 GB) ---
RUN aria2c -x16 -s16 -d models/diffusion_models -o hunyuanvideo1.5_480p_i2v_step_distilled_fp8_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/diffusion_models/hunyuanvideo1.5_480p_i2v_step_distilled_fp8_scaled.safetensors"

# --- Text encoders (9.38 GB + 0.44 GB) ---
RUN aria2c -x16 -s16 -d models/text_encoders -o qwen_2.5_vl_7b_fp8_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"
RUN aria2c -x16 -s16 -d models/text_encoders -o byt5_small_glyphxl_fp16.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/byt5_small_glyphxl_fp16.safetensors"

# --- VAE (~0.5 GB) ---
RUN aria2c -x16 -s16 -d models/vae -o hunyuanvideo15_vae_fp16.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/vae/hunyuanvideo15_vae_fp16.safetensors"

# --- CLIP vision (SigCLIP, ~0.9 GB) ---
RUN aria2c -x16 -s16 -d models/clip_vision -o sigclip_vision_patch14_384.safetensors \
    "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors"

# The base image already sets the correct CMD to start ComfyUI + the RunPod handler.
