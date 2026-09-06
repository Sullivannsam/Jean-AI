#!/usr/bin/env python3
"""
RAG knowledge base — lets the agent answer with your own documents.

Flow:
    ingest(path):  read text/markdown/plaintext files (or a dir), split into
                   chunks, turn each chunk into an embedding via Ollama.
    search(query, k): embed the query, return the k most relevant chunks by
                   cosine similarity.
    add_tool / search_tool: the agent-visible tools that query the index.

Storage: the embeddings live in an index.pkl next to your documents. If the
embedding model isn't available, it falls back to a simple keyword scorer so
the agent still works offline.

Fully local — nothing leaves the machine. Beware: on a CPU-only box, embedding
many files is slow, so ingest smaller sets (docs/notes) not your whole disk.
"""
import json
import os
import pickle
import re
from pathlib import Path

import numpy as np
import requests

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", "knowledge"))
INDEX_PATH = Path(os.getenv("KNOWLEDGE_INDEX", "knowledge/index.pkl"))

# Filenames we load by default. Add more by setting KNOWLEDGE_EXTS in .env
# (comma-separated, e.g. ".txt,.md,.csv,.py"). Never load binaries.
_ALLOWED_EXTS = {e.lower() for e in os.getenv("KNOWLEDGE_EXTS", ".txt,.md,.markdown,.csv").split(",") if e}
MAX_CHUNK_CHARS = 1200
OVERLAP_CHARS = 150


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _split_text(text: str) -> list[str]:
    """Split text into overlapping chunks on paragraph boundaries."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split into logical blocks (paragraphs / blank-line separated)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for p in paras:
        # A single huge paragraph gets hard-wrapped to MAX_CHUNK_CHARS.
        if len(p) > MAX_CHUNK_CHARS:
            p = _wrap(p, MAX_CHUNK_CHARS)
        if len(current) + len(p) + 1 <= MAX_CHUNK_CHARS:
            current = (current + "\n" + p).strip()
        else:
            if current:
                chunks.append(current)
            if len(p) > MAX_CHUNK_CHARS:
                # keep appending remainder as own chunk
                chunks.append(p)
                current = ""
            else:
                current = p
    if current:
        chunks.append(current)
    # Add small overlap for continuity across the boundary
    if len(chunks) > 1:
        merged: list[str] = []
        for i, c in enumerate(chunks):
            if i > 0 and OVERLAP_CHARS > 0:
                c = chunks[i - 1][-OVERLAP_CHARS:] + "\n" + c
            merged.append(c)
        chunks = merged
    return chunks


def _wrap(text: str, width: int) -> str:
    words = text.split()
    lines = []
    line = ""
    for w in words:
        if len(line) + len(w) + 1 > width:
            if line:
                lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Embeddings via Ollama
# ---------------------------------------------------------------------------

def _embed_available() -> bool:
    try:
        resp = requests.get(OLLAMA_URL.replace("/api/chat", "/api/tags"), timeout=5)
        resp.raise_for_status()
        names = [m.get("name", "") for m in resp.json().get("models", [])]
        return any(EMBED_MODEL in n for n in names)
    except Exception:
        return False


def _embed(texts: list[str]) -> list[list[float]] | None:
    """Embed a list of texts with Ollama's /api/embed endpoint. Returns None on
    failure so callers can fall back to keyword scoring."""
    try:
        resp = requests.post(
            OLLAMA_URL.replace("/api/chat", "/api/embed"),
            json={"model": EMBED_MODEL, "input": texts},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Keyword fallback (works offline if no embedding model)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def _keyword_score(query_tokens: set[str], chunk: str) -> float:
    ct = _tokenize(chunk)
    if not ct:
        return 0.0
    return len(query_tokens & ct) / float(len(query_tokens) + 1e-6) if query_tokens else 0.0


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

class KnowledgeBase:
    def __init__(self):
        self.chunks: list[str] = []
        self.sources: list[str] = []
        self.vectors: list[list[float]] = []  # empty if using keyword fallback
        self.embed_mode = False

    def _load(self):
        if INDEX_PATH.exists():
            with open(INDEX_PATH, "rb") as f:
                data = pickle.load(f)
            self.chunks = data.get("chunks", [])
            self.sources = data.get("sources", [])
            self.vectors = data.get("vectors", [])
            self.embed_mode = bool(self.vectors)

    def _save(self):
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_PATH, "wb") as f:
            pickle.dump(
                {"chunks": self.chunks, "sources": self.sources, "vectors": self.vectors},
                f,
            )

    def ingest(self, path: str) -> dict:
        p = Path(path)
        if p.is_dir():
            files = [f for f in p.rglob("*") if f.suffix.lower() in _ALLOWED_EXTS]
        else:
            files = [p] if p.suffix.lower() in _ALLOWED_EXTS else []
        if not files:
            return {"error": f"No {sorted(_ALLOWED_EXTS)} files found at {path}"}

        new_chunks: list[str] = []
        new_sources: list[str] = []
        existing = set(zip(self.sources, self.chunks)) if self.chunks else set()
        for f in files:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for c in _split_text(text):
                if (str(f), c) in existing:
                    continue  # skip duplicates on re-ingest (keeps index from bloating)
                existing.add((str(f), c))
                new_chunks.append(c)
                new_sources.append(str(f))

        if not new_chunks:
            return {"status": "no chunks ingested", "path": str(p)}

        embed_mode = _embed_available()
        if embed_mode:
            vecs = _embed(new_chunks)
            if not vecs or len(vecs) != len(new_chunks):
                embed_mode = False
        else:
            vecs = None

        self.chunks += new_chunks
        self.sources += new_sources
        if embed_mode and vecs:
            self.vectors += vecs
            self.embed_mode = True

        self._save()
        return {
            "status": "ingested",
            "files": len(files),
            "chunks": len(new_chunks),
            "mode": "embeddings" if embed_mode else "keyword",
            "total_chunks": len(self.chunks),
        }

    def search(self, query: str, k: int = 3) -> list[dict]:
        if not self.chunks:
            return []

        if self.embed_mode and self.vectors:
            qv = _embed([query])
            if qv and len(qv) == 1:
                q = np.array(qv[0])
                mat = np.array(self.vectors)
                # cosine similarity (rows normalized)
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                norms[norms == 0] = 1
                scores = (mat @ q) / (norms[:, 0] * (np.linalg.norm(q) or 1))
                order = np.argsort(-scores)[:k]
                return [
                    {"text": self.chunks[i], "source": self.sources[i], "score": float(scores[i])}
                    for i in order
                ]

        # keyword fallback
        qt = _tokenize(query)
        scored = [(chunk, src, _keyword_score(qt, chunk)) for chunk, src in zip(self.chunks, self.sources)]
        scored.sort(key=lambda x: x[2], reverse=True)
        return [
            {"text": t, "source": s, "score": sc}
            for t, s, sc in scored[:k]
            if sc > 0
        ]

    def stats(self) -> dict:
        return {
            "total_chunks": len(self.chunks),
            "mode": "embeddings" if self.embed_mode else "keyword",
            "embed_model": EMBED_MODEL if self.embed_mode else None,
            "index_path": str(INDEX_PATH),
        }


# ---------------------------------------------------------------------------
# Agent-facing tools
# ---------------------------------------------------------------------------

_kb: KnowledgeBase | None = None


def _get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
        _kb._load()
    return _kb


def kb_search(query: str, k: int = 3) -> dict:
    """Search your knowledge base and return the top chunks. Call this before
    answering when the question might involve your personal docs."""
    kb = _get_kb()
    if not kb.chunks:
        return {"error": "Knowledge base is empty. Ingest files first (set KNOWLEDGE_DIR in .env) or run ingest."}
    results = kb.search(query, k=int(k))
    return {"results": results}


def kb_ingest(path: str | None = None) -> dict:
    """Ingest a file or folder into the knowledge base. Defaults to KNOWLEDGE_DIR."""
    target = path or str(KNOWLEDGE_DIR)
    return _get_kb().ingest(target)


def kb_stats() -> dict:
    return {"knowledge": _get_kb().stats()}


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "ingest":
        print(kb_ingest(sys.argv[2] if len(sys.argv) > 2 else None))
    elif cmd == "search":
        print(kb_search(sys.argv[2] if len(sys.argv) > 2 else ""))
    else:
        print(kb_stats())