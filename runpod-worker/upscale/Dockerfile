# SUPIR image-upscale serverless worker for RunPod.
# Base: RunPod's official ComfyUI serverless worker (ComfyUI + handler, no models).
#
# The workflow's SUPIR nodes (SUPIRApply, ModelPatchLoader) are NATIVE to recent
# ComfyUI (merged via Comfy-Org/ComfyUI PR #13250). The only third-party pack it
# needs is KJNodes (for BOOLConstant). We bake the 3 required models (~16 GB).
#
# ⚠️ VERIFY FIRST: confirm this base's ComfyUI actually has SUPIRApply. If a job
# fails with "node type not found: SUPIRApply", the base's ComfyUI predates the
# SUPIR merge — use a newer worker-comfyui tag (or update ComfyUI in this image).
FROM runpod/worker-comfyui:5.10.0-base

# git = clone custom nodes (RunPod's builder has NO git; GHCR/Actions does); aria2 = fast big-model DL.
RUN apt-get update && apt-get install -y --no-install-recommends git aria2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /comfyui

# --- Custom node: KJNodes (provides BOOLConstant used by the captioning switch) ---
RUN git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes.git \
      custom_nodes/ComfyUI-KJNodes \
    && pip install -r custom_nodes/ComfyUI-KJNodes/requirements.txt

RUN mkdir -p models/checkpoints models/model_patches models/text_encoders

# --- Models (~16 GB total). Downloads happen ONCE, at build time. ---
# SDXL checkpoint (~6.6 GB) -> models/checkpoints/
RUN aria2c -x16 -s16 -d models/checkpoints -o juggernautXL_v9Rdphoto2Lightning.safetensors \
    "https://huggingface.co/AiWise/Juggernaut-XL-V9-GE-RDPhoto2-Lightning_4S/resolve/main/juggernautXL_v9Rdphoto2Lightning.safetensors"

# SUPIR model patch (~1.3 GB) -> models/model_patches/
RUN aria2c -x16 -s16 -d models/model_patches -o SUPIR-v0Q_fp16.safetensors \
    "https://huggingface.co/Kijai/SUPIR_pruned/resolve/main/SUPIR-v0Q_fp16.safetensors"

# Qwen3.5 4B text encoder / captioner (~8 GB) -> models/text_encoders/
RUN aria2c -x16 -s16 -d models/text_encoders -o qwen3.5_4b_bf16.safetensors \
    "https://huggingface.co/Comfy-Org/Qwen3.5/resolve/main/text_encoders/qwen3.5_4b_bf16.safetensors"

# The base image already sets the correct CMD to start ComfyUI + the RunPod handler.
