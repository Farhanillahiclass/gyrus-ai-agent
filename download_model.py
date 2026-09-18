"""
download_model.py — downloads a local AI model automatically, so "download
it into the project" is one command instead of a manual browser download.

No API key needed — Hugging Face model files are public downloads; only
generating TEXT via their Inference API needs a key (and that's the part
that wasn't working). Downloading a model FILE to run yourself is different
and doesn't touch that API at all.

Usage:
    python download_model.py            # downloads the default (~1GB, good balance)
    python download_model.py --size small   # ~0.7GB, faster/weaker
    python download_model.py --size large   # ~2GB, best quality, needs more RAM
"""

import argparse
import sys
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / "models"

# Each entry: (HF repo, filename, approx size) — all Apache/MIT-licensed
# open-weights models, small enough to download and run on a normal laptop CPU.
OPTIONS = {
    "small": ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "qwen2.5-1.5b-instruct-q4_k_m.gguf", "~1.0 GB"),
    "medium": ("Qwen/Qwen2.5-3B-Instruct-GGUF", "qwen2.5-3b-instruct-q4_k_m.gguf", "~2.0 GB"),
    "large": ("bartowski/Meta-Llama-3.1-8B-Instruct-GGUF", "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf", "~4.9 GB"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "medium", "large"], default="medium",
                         help="small=~1GB fastest, medium=~2GB balanced (default), large=~5GB best quality")
    args = parser.parse_args()

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("Missing dependency. Run: pip install huggingface_hub")
        sys.exit(1)

    repo, filename, size = OPTIONS[args.size]
    MODELS_DIR.mkdir(exist_ok=True)

    existing = list(MODELS_DIR.glob("*.gguf"))
    if existing:
        print(f"A model already exists: {existing[0].name}")
        answer = input("Download another one anyway? (y/N): ").strip().lower()
        if answer != "y":
            print("Skipped.")
            return

    print(f"Downloading {filename} ({size}) from {repo}...")
    print("This is a one-time download — no API key required, it's a public file.")
    try:
        path = hf_hub_download(repo_id=repo, filename=filename, local_dir=str(MODELS_DIR))
        print(f"\nDone. Model saved to: {path}")
        print("Set AI_PROVIDER=local in .env (if not already), then run main.py or server.py.")
    except Exception as e:
        print(f"\nDownload failed: {e}")
        print("If this keeps failing, download the file manually from:")
        print(f"  https://huggingface.co/{repo}/blob/main/{filename}")
        print(f"and place it in: {MODELS_DIR}")


if __name__ == "__main__":
    main()
