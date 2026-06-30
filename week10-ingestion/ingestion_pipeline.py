"""
Week 6 — Incremental ingestion pipeline (file-based demo).

Simulates: full ingest → incremental update → document removal.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_ROOT = ROOT / "data" / "ingestion_corpus"


@dataclass
class ChunkRecord:
    doc_id: str
    chunk_id: str
    text: str
    version: int


@dataclass
class IngestionIndex:
    chunks: dict[str, ChunkRecord] = field(default_factory=dict)
    doc_versions: dict[str, int] = field(default_factory=dict)
    ingest_log: list[dict] = field(default_factory=list)

    def _log(self, action: str, doc_id: str, version: int, chunk_ids: list[str]):
        self.ingest_log.append(
            {
                "action": action,
                "doc_id": doc_id,
                "version": version,
                "chunk_ids": chunk_ids,
            }
        )


def load_doc_file(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def full_ingest(directory: Path) -> IngestionIndex:
    index = IngestionIndex()
    for path in sorted(directory.glob("*.json")):
        if path.name == "manifest.json":
            continue
        ingest_document(index, load_doc_file(path), action="full_ingest")
    return index


def ingest_document(index: IngestionIndex, doc: dict, action: str = "incremental_upsert") -> None:
    doc_id = doc["doc_id"]
    version = doc["version"]
    chunk_ids = []

    # Remove stale chunks for this document before inserting new version
    stale = [cid for cid, rec in index.chunks.items() if rec.doc_id == doc_id]
    for cid in stale:
        del index.chunks[cid]

    for chunk in doc["chunks"]:
        record = ChunkRecord(
            doc_id=doc_id,
            chunk_id=chunk["chunk_id"],
            text=chunk["text"],
            version=version,
        )
        index.chunks[chunk["chunk_id"]] = record
        chunk_ids.append(chunk["chunk_id"])

    index.doc_versions[doc_id] = version
    index._log(action, doc_id, version, chunk_ids)


def apply_incremental_batch(index: IngestionIndex, directory: Path) -> IngestionIndex:
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        manifest = load_doc_file(manifest_path)
        for doc_id in manifest.get("remove_doc_ids", []):
            remove_document(index, doc_id)

    for path in sorted(directory.glob("*.json")):
        if path.name == "manifest.json":
            continue
        ingest_document(index, load_doc_file(path), action="incremental_upsert")
    return index


def remove_document(index: IngestionIndex, doc_id: str) -> None:
    removed = [cid for cid, rec in index.chunks.items() if rec.doc_id == doc_id]
    for cid in removed:
        del index.chunks[cid]
    if doc_id in index.doc_versions:
        del index.doc_versions[doc_id]
    index._log("remove", doc_id, 0, removed)


def get_chunk(index: IngestionIndex, chunk_id: str) -> ChunkRecord | None:
    return index.chunks.get(chunk_id)


def search_by_doc(index: IngestionIndex, doc_id: str) -> list[ChunkRecord]:
    return [c for c in index.chunks.values() if c.doc_id == doc_id]
