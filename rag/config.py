from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / ".models" / "all-MiniLM-L6-v2"
MODEL_MANIFEST = ROOT / "evidence" / "model_manifest.json"
DB_DIR = ROOT / ".runtime" / "rag" / "chroma"
QUERY_FILE = ROOT / "evaluation" / "rag_queries.json"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 60
SENTENCES_PER_CHUNK = 2
TOP_K = 3


def offline_settings() -> None:
    """Configure libraries before import, without changing the user's HOME."""
    os.environ.update({
        "MOCK_LLM": "true", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1", "HF_HUB_DISABLE_XET": "1",
        "HF_HOME": str(ROOT / ".cache" / "huggingface"),
        "TORCH_HOME": str(ROOT / ".cache" / "torch"),
        "TOKENIZERS_PARALLELISM": "false", "ANONYMIZED_TELEMETRY": "false",
        "CREWAI_DISABLE_TELEMETRY": "true", "OTEL_SDK_DISABLED": "true",
        "CREWAI_TRACING_ENABLED": "false",
    })
