"""Local SentenceTransformers + actual persistent Chroma upsert/query."""

import hashlib
import json
import math
from pathlib import Path

from rag.config import DB_DIR, MODEL_DIR, MODEL_MANIFEST, TOP_K, offline_settings

offline_settings()

import chromadb
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from rag.chunking import Chunk, Document, make_chunks


def verify_local_model(directory: Path = MODEL_DIR) -> dict:
    if not directory.is_dir() or not MODEL_MANIFEST.is_file():
        raise FileNotFoundError("Local model missing; run scripts.download_embedding_model during online setup")
    manifest = json.loads(MODEL_MANIFEST.read_text())
    for filename, expected in manifest["files"].items():
        path = directory / filename
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
            raise ValueError(f"Local model integrity failure: {filename}; rerun explicit setup")
    return manifest


class LocalRAG:
    def __init__(self, documents: list[Document], db_dir: Path = DB_DIR) -> None:
        self.model_manifest = verify_local_model()
        torch.set_num_threads(1)
        torch.manual_seed(0)
        self.model = SentenceTransformer(str(MODEL_DIR), device="cpu", local_files_only=True,
                                        trust_remote_code=False)
        self.model.eval()
        self.documents = documents
        self.chunks = {s: make_chunks(documents, s) for s in ("fixed", "sentence")}
        configuration = {
            "documents": [vars(d) for d in documents],
            "chunks": {s: [vars(c) for c in chunks] for s, chunks in self.chunks.items()},
            "model_revision": self.model_manifest["revision"],
        }
        self.index_fingerprint = hashlib.sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()
        self.client = chromadb.PersistentClient(path=str(db_dir), settings=Settings(anonymized_telemetry=False))
        self.collections = {
            s: self.client.get_or_create_collection(
                name=f"ola_{s}_{self.index_fingerprint[:12]}", embedding_function=None,
                configuration={"hnsw": {"space": "cosine", "num_threads": 1}},
                metadata={"strategy": s, "index_fingerprint": self.index_fingerprint},
            ) for s in self.chunks
        }

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True,
                                    show_progress_bar=False, batch_size=32)
        if not np.isfinite(vectors).all() or vectors.shape != (len(texts), 384):
            raise ValueError("Unexpected embedding dimensions or nonfinite values")
        return vectors

    def upsert_indexes(self) -> dict:
        report = {}
        for strategy, chunks in self.chunks.items():
            collection = self.collections[strategy]
            before = collection.count()
            vectors = self.embed([c.embedding_text for c in chunks])
            collection.upsert(ids=[c.chunk_id for c in chunks], embeddings=vectors.tolist(),
                              documents=[c.text for c in chunks], metadatas=[c.metadata() for c in chunks])
            report[strategy] = {"collection": collection.name, "before": before,
                                "after": collection.count(), "expected_chunks": len(chunks),
                                "dimension": vectors.shape[1], "distance": "cosine"}
        return report

    def retrieve(self, query: str, strategy: str, k: int = TOP_K) -> list[dict]:
        if type(k) is not int or k < 1 or not query.strip():
            raise ValueError("Positive k and a nonempty query are required")
        collection = self.collections[strategy]
        if collection.count() == 0:
            raise ValueError("Index is empty; explicitly upsert before querying")
        vector = self.embed([query])[0]
        result = collection.query(query_embeddings=[vector.tolist()], n_results=min(k, collection.count()),
                                  include=["documents", "metadatas", "distances"])
        hits = []
        for chunk_id, text, metadata, distance in zip(result["ids"][0], result["documents"][0],
                                                      result["metadatas"][0], result["distances"][0]):
            hits.append({"chunk_id": chunk_id, "document_id": metadata["document_id"],
                         "text": text, "metadata": metadata,
                         "cosine_similarity": float(1.0 - distance)})
        return sorted(hits, key=lambda h: (-h["cosine_similarity"], h["chunk_id"]))


FALLBACK = "I don't know based on the available policy documents."


def grounded_answer(hits: list[dict], threshold: float) -> dict:
    """MOCK_LLM: quote only the retrieved passages, with parent citations.

    No answer templates, external facts, label lookup or model inference. Fixed
    character chunks may end mid-sentence, so outputs explicitly call them excerpts.
    """
    if not math.isfinite(threshold) or not -1 <= threshold <= 1:
        raise ValueError("Invalid measured similarity threshold")
    if not hits or hits[0]["cosine_similarity"] < threshold:
        return {"answer": FALLBACK, "fallback": True, "citations": [], "excerpts": []}
    supported = hits
    excerpts = [{"document_id": h["document_id"], "chunk_id": h["chunk_id"], "text": h["text"]}
                for h in supported]
    answer = "Retrieved policy excerpts:\n" + "\n".join(f"[{e['document_id']}] {e['text']}" for e in excerpts)
    return {"answer": answer, "fallback": False,
            "citations": list(dict.fromkeys(e["document_id"] for e in excerpts)), "excerpts": excerpts}
