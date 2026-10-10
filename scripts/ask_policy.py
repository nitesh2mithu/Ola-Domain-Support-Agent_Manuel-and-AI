"""Minimal offline Part 1 query CLI; no crew, session memory, cache or API."""

import argparse
import json

from smoke_tests.runtime import (
    FORBIDDEN_PROCESS_ATTEMPTS, NETWORK_ATTEMPTS, install_offline_audit, prepare_runtime,
)
from rag.config import ROOT, offline_settings

prepare_runtime()
offline_settings()
install_offline_audit()

from rag.chunking import load_documents
from rag.core import LocalRAG, grounded_answer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--strategy", choices=("fixed", "sentence"))
    args = parser.parse_args()
    calibration_path = ROOT / "rag" / "calibration.json"
    if not calibration_path.is_file():
        parser.error("Run tests.milestone_03_acceptance to build indexes and measured calibration first")
    calibration = json.loads(calibration_path.read_text())
    rag = LocalRAG(load_documents())
    if calibration["index_fingerprint"] != rag.index_fingerprint:
        parser.error("Knowledge base or model changed; rebuild indexes and recalibrate explicitly")
    strategy = args.strategy or calibration["recommended_strategy"]
    threshold = calibration["thresholds"][strategy]
    if threshold is None:
        parser.error("Calibration clusters overlap: no approved threshold available")
    hits = rag.retrieve(args.query, strategy, calibration["top_k_chunks"])
    response = grounded_answer(hits, threshold)
    if NETWORK_ATTEMPTS or FORBIDDEN_PROCESS_ATTEMPTS:
        raise RuntimeError("Offline audit observed prohibited activity")
    print(json.dumps({"query": args.query, "strategy": strategy, "threshold": threshold,
                      "retrieved": hits, "response": response,
                      "offline": {"network_attempts": NETWORK_ATTEMPTS,
                                  "child_process_attempts": FORBIDDEN_PROCESS_ATTEMPTS}}, indent=2))


if __name__ == "__main__":
    main()
