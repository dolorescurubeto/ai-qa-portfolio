"""Week 6 — Incremental ingestion pipeline tests."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
INGEST = ROOT / "week10-ingestion"
sys.path.insert(0, str(INGEST))

from ingestion_pipeline import (  # noqa: E402
    CORPUS_ROOT,
    apply_incremental_batch,
    full_ingest,
    get_chunk,
    search_by_doc,
)


@pytest.fixture
def v1_index():
    return full_ingest(CORPUS_ROOT / "v1")


def test_v1_ingest_loads_two_documents(v1_index):
    assert len(v1_index.doc_versions) == 2
    assert v1_index.doc_versions["checking_balance_policy"] == 1


def test_v1_checking_balance_content(v1_index):
    chunk = get_chunk(v1_index, "chk_bal_01")
    assert chunk is not None
    assert "$1,847.32" in chunk.text
    assert chunk.version == 1


def test_v2_incremental_updates_balance(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    chunk = get_chunk(v1_index, "chk_bal_01")
    assert chunk.version == 2
    assert "$1,900.00" in chunk.text
    assert "$1,847.32" not in chunk.text


def test_v2_incremental_updates_transfer_limit(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    chunk = get_chunk(v1_index, "xfer_01")
    assert "$3,500.00" in chunk.text
    assert "$3,000.00" not in chunk.text


def test_v2_ingest_log_records_upserts(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    actions = [e["action"] for e in v1_index.ingest_log if e["doc_id"] == "checking_balance_policy"]
    assert "full_ingest" in actions
    assert "incremental_upsert" in actions


def test_v3_removes_document_from_index(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v3")
    assert search_by_doc(v1_index, "transfer_limit_policy") == []
    assert "transfer_limit_policy" not in v1_index.doc_versions


def test_v3_removed_chunks_not_searchable(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v3")
    assert get_chunk(v1_index, "xfer_01") is None


def test_v3_checking_balance_still_present(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v3")
    chunk = get_chunk(v1_index, "chk_bal_01")
    assert chunk is not None
    assert chunk.version == 2


@pytest.mark.regression
def test_ingest_log_has_remove_event(v1_index):
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v2")
    apply_incremental_batch(v1_index, CORPUS_ROOT / "v3")
    remove_events = [e for e in v1_index.ingest_log if e["action"] == "remove"]
    assert len(remove_events) == 1
    assert remove_events[0]["doc_id"] == "transfer_limit_policy"
