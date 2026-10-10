"""Stable chunks with exact body offsets, separated by strategy."""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import re

from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, ROOT, SENTENCES_PER_CHUNK


@dataclass(frozen=True)
class Document:
    document_id: str
    title: str
    body: str
    source: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    strategy: str
    text: str
    title: str
    source: str
    start: int
    end: int

    @property
    def embedding_text(self) -> str:
        # Same heading augmentation in both strategies; heading is KB evidence.
        return f"{self.title}\n{self.text}"

    def metadata(self) -> dict:
        return {k: v for k, v in asdict(self).items() if k not in ("chunk_id", "text")}


def load_documents(directory: Path = ROOT / "knowledge_base") -> list[Document]:
    documents = []
    for path in sorted(directory.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        title = lines[0].removeprefix("# ").strip()
        body = " ".join(line.strip() for line in lines[1:] if line.strip())
        documents.append(Document(path.stem, title, body, f"knowledge_base/{path.name}"))
    if not documents:
        raise ValueError("No knowledge-base documents available")
    return documents


def _chunk(doc: Document, strategy: str, index: int, start: int, end: int) -> Chunk:
    text = doc.body[start:end]
    digest = hashlib.sha256(f"{doc.title}\n{text}\n{start}:{end}".encode()).hexdigest()[:16]
    return Chunk(f"{doc.document_id}:{strategy}:{index:03d}:{digest}",
                 doc.document_id, strategy, text, doc.title, doc.source, start, end)


def fixed_chunks(doc: Document, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Chunk]:
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("Chunk size must be positive and overlap in [0, size)")
    chunks = []
    start = 0
    while start < len(doc.body):
        end = min(start + size, len(doc.body))
        chunks.append(_chunk(doc, "fixed", len(chunks), start, end))
        if end == len(doc.body):
            break
        start += size - overlap
    return chunks


def sentence_chunks(doc: Document, per_chunk: int = SENTENCES_PER_CHUNK) -> list[Chunk]:
    if type(per_chunk) is not int or per_chunk < 1:
        raise ValueError("Sentences per chunk must be a positive integer")
    # Corpus has no dotted abbreviations; sentence punctuation remains intact.
    spans = list(re.finditer(r"\S.*?[.!?](?=\s|$)|\S.+$", doc.body))
    return [_chunk(doc, "sentence", index // per_chunk,
                   spans[index].start(), spans[min(index + per_chunk - 1, len(spans) - 1)].end())
            for index in range(0, len(spans), per_chunk)]


def make_chunks(documents: list[Document], strategy: str) -> list[Chunk]:
    if strategy not in ("fixed", "sentence"):
        raise ValueError("Unknown chunking strategy")
    chunker = fixed_chunks if strategy == "fixed" else sentence_chunks
    return [chunk for doc in documents for chunk in chunker(doc)]
