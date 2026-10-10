"""Run real offline embeddings/indexing/retrieval/evaluation, not provider mocks.

.venv311/bin/python -m tests.milestone_03_acceptance
"""

import os
import hashlib
import importlib.metadata
import json
from pathlib import Path
import socket
import sys
import unittest

from smoke_tests.runtime import (
    FORBIDDEN_PROCESS_ATTEMPTS, NETWORK_ATTEMPTS, OfflineViolation,
    install_offline_audit, prepare_runtime,
)
from rag.config import MODEL_DIR, ROOT, offline_settings

prepare_runtime()
offline_settings()
install_offline_audit()  # Covers imports, local model loading, indexing and queries.

from rag.chunking import fixed_chunks, load_documents, make_chunks, sentence_chunks
from rag.core import FALLBACK, LocalRAG, grounded_answer, verify_local_model
from rag.evaluation import document_metrics, experiment, labels, markdown_report
import numpy as np


class MilestoneThreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_files_before = sorted(p.relative_to(MODEL_DIR).as_posix() for p in MODEL_DIR.rglob("*") if p.is_file())
        cls.documents = load_documents()
        cls.rag = LocalRAG(cls.documents)
        cls.report = experiment(cls.rag)
        cls.report["versions"] = {p: importlib.metadata.version(p) for p in
            ("sentence-transformers", "transformers", "torch", "chromadb", "numpy", "huggingface-hub")}
        cls.report["python"] = sys.version.split()[0]
        # Save measurements even if a later assertion fails; never hide bad results.
        cls.save_evidence()

    @classmethod
    def save_evidence(cls):
        (ROOT / "evidence" / (os.environ.get("CAPSTONE_EVIDENCE_PREFIX","milestone_03")+"_rag.json")).write_text(json.dumps(cls.report, indent=2, sort_keys=True) + "\n")
        (ROOT / "evidence" / (os.environ.get("CAPSTONE_EVIDENCE_PREFIX","milestone_03")+"_rag.md")).write_text(markdown_report(cls.report))
        deployment = {"index_fingerprint": cls.report["index_fingerprint"],
                      "recommended_strategy": cls.report["recommended_strategy"],
                      "top_k_chunks": cls.report["top_k_chunks"],
                      "thresholds": {s: d["calibration"]["threshold"] for s, d in cls.report["strategies"].items()},
                      "labels_sha256": cls.report["labels_sha256"],
                      "model_revision": cls.report["model"]["revision"]}
        (ROOT / "rag" / "calibration.json").write_text(json.dumps(deployment, indent=2, sort_keys=True) + "\n")

    def test_01_chunk_boundaries_overlap_ids_and_parents(self):
        for doc in self.documents:
            chunks = fixed_chunks(doc)
            for chunk in chunks:
                self.assertEqual(chunk.text, doc.body[chunk.start:chunk.end])
                self.assertLessEqual(len(chunk.text), 300)
                self.assertEqual(chunk.document_id, doc.document_id)
            for left, right in zip(chunks, chunks[1:]):
                self.assertEqual(left.end - right.start, 60)
                self.assertEqual(left.text[-60:], right.text[:60])
            self.assertEqual(chunks[0].start, 0)
            self.assertEqual(chunks[-1].end, len(doc.body))
            sentences = sentence_chunks(doc)
            self.assertEqual(len(sentences), 2)
            self.assertEqual(" ".join(c.text for c in sentences), doc.body)
            for chunk in sentences:
                self.assertTrue(chunk.text.endswith("."))
        for strategy in ("fixed", "sentence"):
            chunks = self.rag.chunks[strategy]
            self.assertEqual(chunks, make_chunks(self.documents, strategy))
            self.assertEqual(len({c.chunk_id for c in chunks}), len(chunks))
            self.assertEqual({c.document_id for c in chunks}, {d.document_id for d in self.documents})
        with self.assertRaises(ValueError):
            fixed_chunks(self.documents[0], size=60, overlap=60)

    def test_02_actual_upserts_are_idempotent_and_embeddings_exist(self):
        names = [c.name for c in self.rag.collections.values()]
        self.assertEqual(len(set(names)), 2)
        for strategy, collection in self.rag.collections.items():
            manifest = self.rag.chunks[strategy]
            self.assertEqual(collection.count(), len(manifest))
            self.assertEqual(self.report["second_upsert"][strategy]["before"], len(manifest))
            stored = collection.get(include=["embeddings", "metadatas", "documents"])
            self.assertEqual(set(stored["ids"]), {c.chunk_id for c in manifest})
            vectors = np.asarray(stored["embeddings"])
            self.assertEqual(vectors.shape, (len(manifest), 384))
            self.assertTrue(np.isfinite(vectors).all())
            np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)
            for chunk_id, metadata, text in zip(stored["ids"], stored["metadatas"], stored["documents"]):
                chunk = next(c for c in manifest if c.chunk_id == chunk_id)
                self.assertEqual(metadata["document_id"], chunk.document_id)
                self.assertEqual(text, chunk.text)

    def test_03_cosine_matches_stored_vectors(self):
        query = labels()["evaluation"][0]["query"]
        qvector = self.rag.embed([query])[0]
        for strategy, collection in self.rag.collections.items():
            hits = self.rag.retrieve(query, strategy)
            self.assertEqual(len(hits), 3)
            for hit in hits:
                stored = collection.get(ids=[hit["chunk_id"]], include=["embeddings"])
                vector = np.asarray(stored["embeddings"][0])
                actual = float(np.dot(qvector, vector) / (np.linalg.norm(qvector) * np.linalg.norm(vector)))
                self.assertAlmostEqual(hit["cosine_similarity"], actual, places=5)

    def test_04_empirical_calibration_separates_observed_clusters(self):
        for strategy, data in self.report["strategies"].items():
            with self.subTest(strategy=strategy):
                cal = data["calibration"]
                self.assertGreaterEqual(sum(m["in_scope"] for m in cal["measurements"]), 3)
                self.assertGreaterEqual(sum(not m["in_scope"] for m in cal["measurements"]), 2)
                self.assertTrue(cal["clusters_separated"], "Overlap: inspect saved measurements; do not invent threshold")
                self.assertTrue(cal["maximum_out_of_scope"] < cal["threshold"] < cal["minimum_in_scope"])
                self.assertAlmostEqual(cal["threshold"], (cal["maximum_out_of_scope"] + cal["minimum_in_scope"]) / 2)

    def test_05_in_scope_answers_fallback_and_verbatim_grounding(self):
        for strategy, data in self.report["strategies"].items():
            self.assertGreaterEqual(sum(c["in_scope"] for c in data["evaluation"]), 5)
            for case in data["evaluation"]:
                with self.subTest(strategy=strategy, query=case["id"]):
                    response = case["response"]
                    self.assertIsNotNone(response)
                    self.assertEqual(response["fallback"], not case["in_scope"])
                    self.assertEqual(response, grounded_answer(case["hits"], data["calibration"]["threshold"]))
                    if case["in_scope"]:
                        self.assertIn(case["hits"][0]["document_id"], case["relevant_documents"])
                        self.assertTrue(response["excerpts"])
                        expected = "Retrieved policy excerpts:\n" + "\n".join(
                            f"[{e['document_id']}] {e['text']}" for e in response["excerpts"])
                        self.assertEqual(response["answer"], expected)
                        for excerpt in response["excerpts"]:
                            self.assertTrue(any(excerpt["chunk_id"] == h["chunk_id"] and excerpt["text"] == h["text"] for h in case["hits"]))
                    else:
                        self.assertEqual(response["answer"], FALLBACK)
                        self.assertEqual(response["citations"], [])

    def test_06_parent_dedup_and_independent_metric_arithmetic(self):
        synthetic = document_metrics([{"document_id": "A"}, {"document_id": "A"}, {"document_id": "B"}], ["A", "C"])
        self.assertEqual(synthetic["precision"], 0.5)
        self.assertEqual(synthetic["recall"], 0.5)
        for data in self.report["strategies"].values():
            for case in data["evaluation"]:
                truth = set(case["relevant_documents"])
                parents = {h["document_id"] for h in case["hits"]}
                count = len(parents & truth)
                self.assertEqual(case["metrics"]["precision"], count / len(parents))
                self.assertEqual(case["metrics"]["recall"], count / len(truth) if truth else None)

    def test_07_model_missing_fails_locally_and_prior_inputs_unchanged(self):
        with self.assertRaises(FileNotFoundError):
            verify_local_model(ROOT / ".models" / "not-installed")
        self.assertEqual(hashlib.sha256((ROOT / "Problem_Statement.md").read_bytes()).hexdigest(),
                         "81e2d0ca4499c1865cf8c9fee41c1ce90825440f3eb7f91593c4c2ab9d89dbd6")
        previous = json.loads((ROOT / "evidence" / "milestone_02_acceptance.json").read_text())
        for policy in previous["policies"]:
            self.assertEqual(hashlib.sha256((ROOT / policy["path"]).read_bytes()).hexdigest(), policy["sha256"])
        self.assertEqual(sorted(p.relative_to(MODEL_DIR).as_posix() for p in MODEL_DIR.rglob("*") if p.is_file()), self.model_files_before)
        verify_local_model()

    def test_08_offline_negative_control_and_zero_runtime_attempts(self):
        self.assertEqual(NETWORK_ATTEMPTS, [])
        self.assertEqual(FORBIDDEN_PROCESS_ATTEMPTS, [])
        with self.assertRaises(OfflineViolation):
            socket.getaddrinfo("offline-control.invalid", 443)
        self.assertEqual(NETWORK_ATTEMPTS, ["socket.getaddrinfo"])
        NETWORK_ATTEMPTS.clear()


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MilestoneThreeTests))
    if hasattr(MilestoneThreeTests, "report"):
        report = MilestoneThreeTests.report
        report["acceptance"] = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                                "passed": result.wasSuccessful(), "network_attempts": NETWORK_ATTEMPTS,
                                "child_process_attempts": FORBIDDEN_PROCESS_ATTEMPTS}
        MilestoneThreeTests.save_evidence()
        print(json.dumps({"versions": report["versions"], "acceptance": report["acceptance"],
              "recommended_strategy": report["recommended_strategy"], "recommendation": report["recommendation"],
              "thresholds": {s: d["calibration"]["threshold"] for s, d in report["strategies"].items()}}, indent=2))
    sys.exit(0 if result.wasSuccessful() else 1)
