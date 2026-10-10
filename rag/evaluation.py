"""Calibration and document-level metrics from preregistered labels."""

import hashlib
import json
from statistics import mean

from rag.config import QUERY_FILE, TOP_K
from rag.core import grounded_answer

LABEL_SHA256 = "b1740a9fc39295b218ac387bd2b39138f8f158080ab39e39049d01a59845c3b7"


def labels() -> dict:
    data = QUERY_FILE.read_bytes()
    if hashlib.sha256(data).hexdigest() != LABEL_SHA256:
        raise ValueError("Preregistered query labels changed; report protocol changes before evaluating")
    return json.loads(data)


def document_metrics(hits: list[dict], relevant: list[str]) -> dict:
    retrieved = list(dict.fromkeys(h["document_id"] for h in hits))
    truth = set(relevant)
    matched = sorted(set(retrieved) & truth)
    tp = len(matched)
    precision = tp / len(retrieved) if retrieved else 0.0
    recall = tp / len(truth) if truth else None
    return {"retrieved_parent_documents": retrieved, "relevant_parent_documents": sorted(truth),
            "matched_documents": matched, "true_positives": tp,
            "precision": precision, "recall": recall,
            "precision_arithmetic": f"{tp}/{len(retrieved)} = {precision:.6f}" if retrieved else "0/0 -> 0 by convention",
            "recall_arithmetic": f"{tp}/{len(truth)} = {recall:.6f}" if truth else "undefined (no relevant documents)"}


def calibrate(rag, strategy: str, cases: list[dict]) -> dict:
    measurements = []
    for case in cases:
        hits = rag.retrieve(case["query"], strategy, k=1)
        measurements.append({**case, "top1_cosine_similarity": hits[0]["cosine_similarity"],
                             "top1_chunk_id": hits[0]["chunk_id"], "top1_document_id": hits[0]["document_id"]})
    in_values = [m["top1_cosine_similarity"] for m in measurements if m["in_scope"]]
    out_values = [m["top1_cosine_similarity"] for m in measurements if not m["in_scope"]]
    minimum_in = min(in_values)
    maximum_out = max(out_values)
    separated = maximum_out < minimum_in
    threshold = (minimum_in + maximum_out) / 2 if separated else None
    return {"measurements": measurements, "minimum_in_scope": minimum_in,
            "maximum_out_of_scope": maximum_out, "gap": minimum_in - maximum_out,
            "clusters_separated": separated, "threshold": threshold,
            "method": "midpoint between maximum out-of-scope and minimum in-scope calibration similarity; no threshold if clusters overlap"}


def experiment(rag) -> dict:
    protocol = labels()
    first_upsert = rag.upsert_indexes()
    second_upsert = rag.upsert_indexes()
    report = {"labels_sha256": LABEL_SHA256, "label_policy": protocol["label_policy"],
              "top_k_chunks": TOP_K, "index_fingerprint": rag.index_fingerprint,
              "model": rag.model_manifest, "first_upsert": first_upsert, "second_upsert": second_upsert,
              "chunk_manifest": {s: [vars(c) for c in chunks] for s, chunks in rag.chunks.items()},
              "strategies": {}}
    for strategy in ("fixed", "sentence"):
        calibration = calibrate(rag, strategy, protocol["calibration"])
        cases = []
        for case in protocol["evaluation"]:
            hits = rag.retrieve(case["query"], strategy)
            response = grounded_answer(hits, calibration["threshold"]) if calibration["threshold"] is not None else None
            cases.append({**case, "hits": hits, "response": response,
                          "metrics": document_metrics(hits, case["relevant_documents"])})
        in_scope_cases = [c for c in cases if c["in_scope"]]
        report["strategies"][strategy] = {
            "calibration": calibration, "evaluation": cases,
            "mean_precision": mean(c["metrics"]["precision"] for c in in_scope_cases),
            "mean_recall": mean(c["metrics"]["recall"] for c in in_scope_cases),
        }
    # Recall first, then precision; on ties preserve complete sentence boundaries.
    selected = max(("fixed", "sentence"), key=lambda s: (
        report["strategies"][s]["mean_recall"], report["strategies"][s]["mean_precision"], s == "sentence"))
    report["recommended_strategy"] = selected
    f, s = report["strategies"]["fixed"], report["strategies"]["sentence"]
    report["recommendation"] = (
        f"Deploy {selected} chunking: fixed chunks achieved mean document precision {f['mean_precision']:.4f} and recall {f['mean_recall']:.4f}, "
        f"while sentence chunks achieved precision {s['mean_precision']:.4f} and recall {s['mean_recall']:.4f} on the same six labelled queries. "
        "Selection prioritizes recall and then precision, with complete sentence boundaries breaking metric ties. "
        "These small-corpus measurements support this deployment choice but do not establish performance on broader or near-domain questions."
    )
    return report


def markdown_report(report: dict) -> str:
    lines = ["# Milestone 3 — RAG evidence", "", f"Labels frozen SHA-256: `{report['labels_sha256']}`.",
             "", "Top-k = 3 chunks; parent documents deduplicated before scoring. Macro means include only six in-scope evaluation queries; fallback queries have no relevant documents and undefined recall.", ""]
    for strategy, data in report["strategies"].items():
        cal = data["calibration"]
        lines += [f"## {strategy} calibration", "", "| ID | In scope | Top-1 cosine | Parent |", "|---|---|---:|---|"]
        lines += [f"| {m['id']} | {m['in_scope']} | {m['top1_cosine_similarity']:.8f} | {m['top1_document_id']} |" for m in cal["measurements"]]
        lines += ["", f"Maximum out-of-scope: {cal['maximum_out_of_scope']:.8f}; minimum in-scope: {cal['minimum_in_scope']:.8f}; gap: {cal['gap']:.8f}; chosen threshold: {cal['threshold']}.",
                  "", f"## {strategy} document-level evaluation", "", "| Query | Relevant parents | Retrieved parents (dedup) | Precision arithmetic | Recall arithmetic |", "|---|---|---|---|---|"]
        for case in data["evaluation"]:
            metrics = case["metrics"]
            lines.append(f"| {case['id']} | {', '.join(metrics['relevant_parent_documents']) or 'none'} | {', '.join(metrics['retrieved_parent_documents'])} | {metrics['precision_arithmetic']} | {metrics['recall_arithmetic']} |")
        lines += ["", f"Mean precision: {data['mean_precision']:.6f}; mean recall: {data['mean_recall']:.6f}.", "", f"## {strategy} actual answers and retrieved context", ""]
        for case in data["evaluation"]:
            lines += [f"### {case['id']}: {case['query']}", ""]
            for hit in case["hits"]:
                lines.append(f"- Chunk `{hit['chunk_id']}`, parent `{hit['document_id']}`, cosine {hit['cosine_similarity']:.8f}.")
            lines += ["", case["response"]["answer"] if case["response"] else "NO THRESHOLD: overlapping calibration clusters; acceptance incomplete.", ""]
    lines += ["## Deployment recommendation", "", report["recommendation"], ""]
    return "\n".join(lines)
