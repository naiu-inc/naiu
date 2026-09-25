# SUPIR image-upscale — RunPod Serverless Worker

Standalone endpoint (separate from HunyuanVideo and frame-interpolation) for
SUPIR image restoration/upscale: SDXL + SUPIR model-patch + a Qwen3.5-4B captioner.

Files in this folder:
- `Dockerfile` — bakes KJNodes + the 3 models (~16 GB).
- `image_upscale_api.json` — the flattened API-format workflow (subgraph expanded).
- `test_upscale_job.py` — fire one job, time it, save the PNG.

## Build & deploy (GHCR, not RunPod's builder)

The image is ~20 GB, so build it on GitHub Actions and push to GHCR (same as the
HunyuanVideo worker), then deploy from the prebuilt image.

1. Workflow: `.github/workflows/build-upscale.yml` → pushes
   `ghcr.io/naiu-inc/naiu-upscale-worker:v1`. Run it from the Actions tab (or it
   triggers on changes to `runpod-worker/upscale/Dockerfile`). Make the GHCR
   package **public**.
2. RunPod → Serverless → New Endpoint → **Deploy from a Docker image** →
   `ghcr.io/naiu-inc/naiu-upscale-worker:v1`.

### Endpoint settings
| Setting | Value | Why |
|---|---|---|
| GPU | 24 GB min (32 GB safer) | SDXL + Qwen-4B + high-res SUPIR |
| Active workers | `0` | scale-to-zero |
| Max workers | `2` | |
| Idle timeout | `10–30` s | jobs are long; keep-alive matters less per job |
| Execution timeout | `600` s | SUPIR is slow (10 steps + LLM caption + high-res) |
| Container disk | `15` GB | large intermediate tiles |

## Verify before trusting the build
Confirm the base ComfyUI has `SUPIRApply` (native via PR #13250). If a job fails
with "node type not found: SUPIRApply", bump the `runpod/worker-comfyui` base tag
(or update ComfyUI in the image).

## Send a job
```powershell
$env:RUNPOD_API_KEY="<key>"
$env:RUNPOD_ENDPOINT_ID="<upscale endpoint id>"
python test_upscale_job.py --image "C:/path/photo.jpg"
# optional: --megapixels 4  --seed 12345
```
Output is a PNG (no video codec involved). Note `executionTime` to price the tier.

## Per-request override points (for the portal later)
Node ids in `image_upscale_api.json` (auto-detected by class_type in the test script):
- `LoadImage` (id `92`) → `inputs.image` = uploaded filename
- `ResizeImageMaskNode` (id `85:94`) → `inputs["resize_type.megapixels"]` = output MP
- `SamplerCustom` (id `85:20`) → `inputs.noise_seed`
- `BasicScheduler` (id `85:29`) → `inputs.steps` / `denoise`

Env var for the portal: `RUNPOD_UPSCALE_ENDPOINT_ID`.
