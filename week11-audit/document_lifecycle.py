"""
Week 7 — Audit logging and document lifecycle traceability.

Lifecycle: upload → ingest → index → query → response
Every step must emit an audit event.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INGEST_DIR = ROOT / "week10-ingestion"
import sys

sys.path.insert(0, str(INGEST_DIR))

from ingestion_pipeline import (  # noqa: E402
    IngestionIndex,
    apply_incremental_batch,
    full_ingest,
    ingest_document,
    load_doc_file,
)

REQUIRED_LIFECYCLE_ACTIONS = [
    "document_uploaded",
    "document_ingested",
    "document_indexed",
    "document_queried",
    "response_returned",
]


@dataclass
class AuditEvent:
    event_id: str
    action: str
    user_id: str
    doc_id: str
    timestamp: str
    metadata: dict = field(default_factory=dict)


@dataclass
class AuditLog:
    events: list[AuditEvent] = field(default_factory=list)

    def record(self, action: str, user_id: str, doc_id: str, **metadata) -> AuditEvent:
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            action=action,
            user_id=user_id,
            doc_id=doc_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata,
        )
        self.events.append(event)
        return event

    def actions_for_doc(self, doc_id: str) -> list[str]:
        return [e.action for e in self.events if e.doc_id == doc_id]

    def export_json(self) -> list[dict]:
        return [asdict(e) for e in self.events]


class DocumentLifecycle:
    def __init__(self, ingestion_index: IngestionIndex | None = None):
        self.ingestion_index = ingestion_index or IngestionIndex()
        self.audit = AuditLog()

    def upload(self, user_id: str, doc_path: Path) -> dict:
        doc = load_doc_file(doc_path)
        self.audit.record(
            "document_uploaded",
            user_id,
            doc["doc_id"],
            source=str(doc_path),
            version=doc.get("version"),
        )
        return doc

    def ingest(self, user_id: str, doc: dict) -> None:
        ingest_document(self.ingestion_index, doc, action="lifecycle_ingest")
        chunk_ids = [c["chunk_id"] for c in doc["chunks"]]
        self.audit.record(
            "document_ingested",
            user_id,
            doc["doc_id"],
            version=doc["version"],
            chunk_count=len(chunk_ids),
        )

    def index_document(self, user_id: str, doc_id: str) -> None:
        chunks = [
            c.chunk_id for c in self.ingestion_index.chunks.values() if c.doc_id == doc_id
        ]
        self.audit.record(
            "document_indexed",
            user_id,
            doc_id,
            chunk_ids=chunks,
            indexed_count=len(chunks),
        )

    def query(self, user_id: str, doc_id: str, query_text: str) -> dict:
        self.audit.record(
            "document_queried",
            user_id,
            doc_id,
            query=query_text,
        )
        matches = [c for c in self.ingestion_index.chunks.values() if c.doc_id == doc_id]
        if not matches:
            response = {"status": "not_found", "doc_id": doc_id}
        else:
            top = matches[0]
            response = {
                "status": "ok",
                "doc_id": doc_id,
                "chunk_id": top.chunk_id,
                "text": top.text,
                "version": top.version,
            }
        self.audit.record(
            "response_returned",
            user_id,
            doc_id,
            response_status=response["status"],
            chunk_id=response.get("chunk_id"),
        )
        return response


def lifecycle_actions_complete(audit: AuditLog, doc_id: str) -> bool:
    actions = set(audit.actions_for_doc(doc_id))
    return all(a in actions for a in REQUIRED_LIFECYCLE_ACTIONS)


def missing_lifecycle_actions(audit: AuditLog, doc_id: str) -> list[str]:
    present = set(audit.actions_for_doc(doc_id))
    return [a for a in REQUIRED_LIFECYCLE_ACTIONS if a not in present]


def validate_event_fields(event: AuditEvent) -> bool:
    return bool(event.event_id and event.action and event.user_id and event.doc_id and event.timestamp)
