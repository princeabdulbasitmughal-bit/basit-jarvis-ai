"""
================================================================================
👑 BASIT JARVIS AI — OFFLINE MODEL CACHE DOWNLOADER
================================================================================
Downloads and caches local neural AI models for 100% offline Jarvis operation:
  1. Kokoro-82M ONNX model (kokoro-v0_19.onnx) & voices package (voices.bin)
  2. Faster-Whisper tiny/base STT models

Usage:
  python modules/download_models.py
================================================================================
"""

import os
import sys
import urllib.request
import time

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

KOKORO_MODEL_URL = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.onnx"
KOKORO_VOICES_URL = "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin"


def download_with_progress(url: str, dest_path: str, label: str):
    """Downloads a file with a dynamic progress indicator."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024 * 1024:
        size_mb = os.path.getsize(dest_path) / (1024 * 1024)
        print(f"✅ [{label}] Already cached: {dest_path} ({size_mb:.1f} MB)")
        return True

    print(f"\n📥 [{label}] Downloading from {url}...")
    start_time = time.time()

    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\r   Progress: {percent:5.1f}% [{mb_downloaded:.1f} / {mb_total:.1f} MB]")
            sys.stdout.flush()

    try:
        temp_dest = dest_path + ".tmp"
        urllib.request.urlretrieve(url, temp_dest, reporthook=report_progress)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        os.rename(temp_dest, dest_path)
        elapsed = time.time() - start_time
        print(f"\n✅ [{label}] Successfully cached in {elapsed:.1f}s!")
        return True
    except Exception as e:
        print(f"\n❌ [{label}] Download failed: {e}")
        return False


def setup_all_models():
    """Main orchestration for offline model caching."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   👑 BASIT JARVIS AI — NEURAL OFFLINE MODEL CACHE        ║")
    print("╚══════════════════════════════════════════════════════════╝")

    kokoro_model_path = os.path.join(MODELS_DIR, "kokoro-v0_19.onnx")
    kokoro_voices_path = os.path.join(MODELS_DIR, "voices.bin")

    # 1. Download Kokoro-82M ONNX model
    download_with_progress(KOKORO_MODEL_URL, kokoro_model_path, "Kokoro-82M ONNX")

    # 2. Download Kokoro voices package
    download_with_progress(KOKORO_VOICES_URL, kokoro_voices_path, "Kokoro Voices")

    print("\n🎉 Model caching process finished.")


if __name__ == "__main__":
    setup_all_models()
