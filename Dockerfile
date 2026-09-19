# HunyuanVideo 1.5 i2v serverless worker for RunPod
# Base: RunPod's official ComfyUI serverless worker (ComfyUI + handler, no models)
# We bake in the 5 models so workers never download from Hugging Face at runtime.
FROM runpod/worker-comfyui:5.10.0-base

# ComfyUI lives at /comfyui in this base image.
WORKDIR /comfyui

# Make sure the model subfolders exist, then download each weight into place.
# Downloads happen ONCE, at build time. The result is baked into the image.
RUN mkdir -p models/diffusion_models models/text_encoders models/vae models/clip_vision

# --- Diffusion model (UNet): 480p i2v step-distilled, fp8  (8.34 GB) ---
RUN wget -q --show-progress -O models/diffusion_models/hunyuanvideo1.5_480p_i2v_step_distilled_fp8_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/diffusion_models/hunyuanvideo1.5_480p_i2v_step_distilled_fp8_scaled.safetensors"

# --- Text encoders (9.38 GB + 0.44 GB) ---
RUN wget -q --show-progress -O models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"
RUN wget -q --show-progress -O models/text_encoders/byt5_small_glyphxl_fp16.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/byt5_small_glyphxl_fp16.safetensors"

# --- VAE (~0.5 GB) ---
RUN wget -q --show-progress -O models/vae/hunyuanvideo15_vae_fp16.safetensors \
    "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/vae/hunyuanvideo15_vae_fp16.safetensors"

# --- CLIP vision (SigCLIP, ~0.9 GB) ---
RUN wget -q --show-progress -O models/clip_vision/sigclip_vision_patch14_384.safetensors \
    "https://huggingface.co/Comfy-Org/sigclip_vision_384/resolve/main/sigclip_vision_patch14_384.safetensors"

# The base image already sets the correct CMD to start ComfyUI + the RunPod handler.
