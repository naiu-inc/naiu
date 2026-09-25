#!/usr/bin/env python3
"""
Fire one SUPIR image-upscale job at the RunPod serverless endpoint and time it.

Usage (PowerShell) - set your OWN key/endpoint as env vars, do NOT hardcode them:
  $env:RUNPOD_API_KEY="<your_key>"
  $env:RUNPOD_ENDPOINT_ID="<your_upscale_endpoint_id>"
  python test_upscale_job.py --image "C:/path/photo.jpg"

Defaults to image_upscale_api.json in this folder (the flattened API-format export).
Node ids are auto-detected by class_type, so it survives subgraph re-numbering.

Optional overrides: --seed, --megapixels (final output megapixels).
Uploads the image, injects it into the LoadImage node, submits, polls, saves PNGs.
"""
import argparse, base64, json, os, random, sys, time
from pathlib import Path
import urllib.request

HERE = Path(__file__).parent
DEFAULT_WORKFLOW = HERE / "image_upscale_api.json"


def http_post(url, api_key, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def http_get(url, api_key):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def find_nodes(wf, class_type):
    """Return [(node_id, node_dict), ...] for every node of the given class_type."""
    return [(nid, n) for nid, n in wf.items() if isinstance(n, dict) and n.get("class_type") == class_type]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="input image path")
    ap.add_argument("--workflow", default=str(DEFAULT_WORKFLOW), help="API-format SUPIR workflow JSON")
    ap.add_argument("--seed", type=int, default=None, help="override SamplerCustom noise_seed")
    ap.add_argument("--megapixels", type=float, default=None, help="override final output megapixels (ResizeImageMaskNode)")
    args = ap.parse_args()

    api_key = os.environ.get("RUNPOD_API_KEY")
    endpoint = os.environ.get("RUNPOD_ENDPOINT_ID")
    if not api_key or not endpoint:
        sys.exit("Set RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID env vars first.")

    wf = json.loads(Path(args.workflow).read_text())

    # --- inject the uploaded image into every LoadImage node ---
    loaders = find_nodes(wf, "LoadImage")
    if not loaders:
        sys.exit("No LoadImage node found — is this the flattened API-format export?")
    img_name = "input" + Path(args.image).suffix
    for _, n in loaders:
        n["inputs"]["image"] = img_name

    # --- seed: use --seed, else randomize so repeat runs differ ---
    seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)
    for _, n in find_nodes(wf, "SamplerCustom"):
        n["inputs"]["noise_seed"] = seed
    print(f"seed: {seed}")

    # --- optional: final output megapixels ---
    if args.megapixels is not None:
        for _, n in find_nodes(wf, "ResizeImageMaskNode"):
            for k in list(n["inputs"].keys()):
                if k.endswith("megapixels"):
                    n["inputs"][k] = args.megapixels

    img_b64 = base64.b64encode(Path(args.image).read_bytes()).decode()
    payload = {"input": {"workflow": wf, "images": [{"name": img_name, "image": img_b64}]}}

    base = f"https://api.runpod.ai/v2/{endpoint}"
    print(f"Workflow: {Path(args.workflow).name}  |  LoadImage nodes: {[nid for nid, _ in loaders]}")
    print("Submitting job...")
    t0 = time.time()
    job = http_post(f"{base}/run", api_key, payload)
    job_id = job["id"]
    print(f"Job id: {job_id}  (status: {job.get('status')})")

    last = None
    while True:
        s = http_get(f"{base}/status/{job_id}", api_key)
        st = s.get("status")
        if st != last:
            print(f"  [{time.time()-t0:6.1f}s] status: {st}")
            last = st
        if st in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
            break
        time.sleep(3)

    elapsed = time.time() - t0
    print(f"\nTotal wall time: {elapsed:.1f}s  |  delayTime={s.get('delayTime')}  executionTime={s.get('executionTime')}")

    if st != "COMPLETED":
        print("Job did not complete:", json.dumps(s, indent=2)[:2000]); return

    out = s.get("output", {})
    saved = False
    for i, item in enumerate(out.get("images") or []):
        data = item.get("data") or item.get("image")
        if data and item.get("type", "").lower() in ("base64", ""):
            fn = item.get("filename", f"upscaled_{i}.png")
            Path(fn).write_bytes(base64.b64decode(data))
            print("Saved:", fn); saved = True
        elif item.get("type", "").lower() == "s3_url" or str(data).startswith("http"):
            print("Output URL:", data); saved = True
    if not saved:
        print("Raw output (inspect format):", json.dumps(out, indent=2)[:2000])


if __name__ == "__main__":
    main()
