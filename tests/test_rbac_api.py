"""Week 5 — RBAC and REST API tests."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
API_DIR = ROOT / "week09-rbac-api"
sys.path.insert(0, str(API_DIR))

from app import app  # noqa: E402

USERS = json.load(open(ROOT / "data" / "rbac_users.json", encoding="utf-8"))
TOKENS = {u["role"]: u["token"] for u in USERS}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def auth_headers(role: str) -> dict:
    return {"Authorization": f"Bearer {TOKENS[role]}"}


def test_health_no_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_balance_analyst_ok(client):
    r = client.get("/api/v1/account/balance", headers=auth_headers("analyst"))
    assert r.status_code == 200
    body = r.get_json()
    assert body["balance"] == "$1,847.32"
    assert body["role"] == "analyst"


def test_balance_auditor_forbidden(client):
    r = client.get("/api/v1/account/balance", headers=auth_headers("auditor"))
    assert r.status_code == 403
    assert r.get_json()["error"] == "forbidden"


def test_balance_guest_forbidden(client):
    r = client.get("/api/v1/account/balance", headers=auth_headers("guest"))
    assert r.status_code == 403


def test_balance_missing_token_unauthorized(client):
    r = client.get("/api/v1/account/balance")
    assert r.status_code == 401


def test_audit_logs_auditor_ok(client):
    r = client.get("/api/v1/audit/logs", headers=auth_headers("auditor"))
    assert r.status_code == 200
    body = r.get_json()
    assert body["count"] == 2
    assert body["events"][0]["event_id"] == "evt_001"


def test_audit_logs_analyst_forbidden(client):
    r = client.get("/api/v1/audit/logs", headers=auth_headers("analyst"))
    assert r.status_code == 403


def test_transfer_limit_manager_ok(client):
    r = client.get("/api/v1/transfer/limit", headers=auth_headers("manager"))
    assert r.status_code == 200
    assert r.get_json()["daily_transfer_limit"] == "$3,000.00"


def test_transfer_limit_analyst_forbidden(client):
    r = client.get("/api/v1/transfer/limit", headers=auth_headers("analyst"))
    assert r.status_code == 403


@pytest.mark.parametrize(
    "role,expected_keys",
    [
        ("analyst", {"doc_id", "title", "summary", "account_type"}),
        ("manager", {"doc_id", "title", "summary", "account_type", "balance", "internal_risk_flag", "audit_trail_id"}),
        ("auditor", {"doc_id", "title", "audit_trail_id"}),
    ],
)
def test_document_filtered_view_by_role(client, role, expected_keys):
    r = client.get(
        "/api/v1/documents/doc_checking_001",
        headers=auth_headers(role),
    )
    assert r.status_code == 200
    body = r.get_json()
    assert set(body.keys()) == expected_keys


def test_document_analyst_cannot_see_balance_field(client):
    r = client.get(
        "/api/v1/documents/doc_checking_001",
        headers=auth_headers("analyst"),
    )
    body = r.get_json()
    assert "balance" not in body
    assert "internal_risk_flag" not in body


def test_document_manager_sees_sensitive_fields(client):
    r = client.get(
        "/api/v1/documents/doc_checking_001",
        headers=auth_headers("manager"),
    )
    body = r.get_json()
    assert body["balance"] == "$1,847.32"
    assert body["internal_risk_flag"] == "low"


def test_document_guest_forbidden(client):
    r = client.get(
        "/api/v1/documents/doc_checking_001",
        headers=auth_headers("guest"),
    )
    assert r.status_code == 403
