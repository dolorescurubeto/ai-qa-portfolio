# Week 6 notes — Ingestion pipeline

## Why incremental?

Re-indexing **everything** on every change is slow and risky. Production systems ingest **only what changed**.

| Action | What happens to index |
|--------|------------------------|
| New doc | Add chunks |
| Updated doc | Delete old chunks for doc_id → insert v2 |
| Removed doc | Delete all chunks for doc_id |

## What tests catch

| Bug | Test |
|-----|------|
| Stale content after update | v2 still shows $1,847.32 |
| Orphan chunks after delete | xfer_01 still searchable after v3 |
| Missing audit of ingest | no `remove` event in ingest_log |

## Connection to RAG Week 2

Retrieval is only as good as the index. If v2 update fails silently, RAG answers with **old policy** → wrong customer info.

## Interview line

> "I test incremental ingestion: upsert replaces stale chunks by doc_id, removals purge all chunk_ids, and ingest logs record every action for traceability."
