"""Explicit online setup only; never imported by RAG runtime."""

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_DIR = ROOT / ".models" / "all-MiniLM-L6-v2"
os.environ["HF_HOME"] = str(ROOT / ".cache" / "huggingface")
os.environ["HF_HUB_DISABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from huggingface_hub import HfApi, snapshot_download


def main() -> None:
    manifest_path = ROOT / "evidence" / "milestone_03_model_manifest.json"
    # Re-running setup preserves the original revision, rather than following main.
    revision = json.loads(manifest_path.read_text())["revision"] if manifest_path.exists() else HfApi(token=False).model_info(MODEL_ID).sha
    snapshot_download(repo_id=MODEL_ID, revision=revision, local_dir=MODEL_DIR,
                      cache_dir=ROOT / ".cache" / "huggingface", token=False,
                      allow_patterns=["*.json", "*.txt", "model.safetensors", "1_Pooling/config.json"])
    files = {}
    for path in sorted(MODEL_DIR.rglob("*")):
        if path.is_file() and ".cache" not in path.relative_to(MODEL_DIR).parts:
            files[path.relative_to(MODEL_DIR).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    manifest = {"model_id": MODEL_ID, "revision": revision,
                "local_path": MODEL_DIR.relative_to(ROOT).as_posix(), "files": files,
                "setup_network_required": True, "runtime_network_required": False}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
