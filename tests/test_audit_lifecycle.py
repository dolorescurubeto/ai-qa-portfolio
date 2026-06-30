"""Week 7 — Audit logging and document lifecycle tests."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "week11-audit"
sys.path.insert(0, str(AUDIT_DIR))

from document_lifecycle import (  # noqa: E402
    DocumentLifecycle,
    REQUIRED_LIFECYCLE_ACTIONS,
    lifecycle_actions_complete,
    missing_lifecycle_actions,
    validate_event_fields,
)

CORPUS = ROOT / "data" / "ingestion_corpus"
DOC_V1 = CORPUS / "v1" / "checking_balance_policy.json"
USER = "user_analyst_01"
DOC_ID = "checking_balance_policy"


@pytest.fixture
def lifecycle():
    return DocumentLifecycle()


def run_full_lifecycle(lc: DocumentLifecycle) -> dict:
    doc = lc.upload(USER, DOC_V1)
    lc.ingest(USER, doc)
    lc.index_document(USER, DOC_ID)
    return lc.query(USER, DOC_ID, "what is the checking balance")


def test_upload_creates_audit_event(lifecycle):
    lifecycle.upload(USER, DOC_V1)
    assert len(lifecycle.audit.events) == 1
    assert lifecycle.audit.events[0].action == "document_uploaded"


def test_full_lifecycle_emits_five_events(lifecycle):
    run_full_lifecycle(lifecycle)
    assert len(lifecycle.audit.events) == 5


@pytest.mark.regression
def test_lifecycle_actions_complete(lifecycle):
    run_full_lifecycle(lifecycle)
    assert lifecycle_actions_complete(lifecycle.audit, DOC_ID)
    assert missing_lifecycle_actions(lifecycle.audit, DOC_ID) == []


@pytest.mark.parametrize("action", REQUIRED_LIFECYCLE_ACTIONS)
def test_each_required_action_present(lifecycle, action):
    run_full_lifecycle(lifecycle)
    actions = lifecycle.audit.actions_for_doc(DOC_ID)
    assert action in actions


def test_events_have_required_fields(lifecycle):
    run_full_lifecycle(lifecycle)
    for event in lifecycle.audit.events:
        assert validate_event_fields(event)


def test_query_response_contains_indexed_content(lifecycle):
    response = run_full_lifecycle(lifecycle)
    assert response["status"] == "ok"
    assert "$1,847.32" in response["text"]


def test_response_returned_event_metadata(lifecycle):
    run_full_lifecycle(lifecycle)
    response_events = [e for e in lifecycle.audit.events if e.action == "response_returned"]
    assert response_events[0].metadata["response_status"] == "ok"


def test_queried_event_stores_query_text(lifecycle):
    run_full_lifecycle(lifecycle)
    query_events = [e for e in lifecycle.audit.events if e.action == "document_queried"]
    assert "checking balance" in query_events[0].metadata["query"]


def test_incomplete_lifecycle_detected_when_index_skipped():
    lc = DocumentLifecycle()
    doc = lc.upload(USER, DOC_V1)
    lc.ingest(USER, doc)
    lc.query(USER, DOC_ID, "balance")
    missing = missing_lifecycle_actions(lc.audit, DOC_ID)
    assert "document_indexed" in missing
    assert not lifecycle_actions_complete(lc.audit, DOC_ID)


def test_audit_export_json_serializable(lifecycle):
    run_full_lifecycle(lifecycle)
    exported = lifecycle.audit.export_json()
    assert len(exported) == 5
    assert all("event_id" in e and "timestamp" in e for e in exported)
