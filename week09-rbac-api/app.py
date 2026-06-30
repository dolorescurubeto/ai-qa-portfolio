"""
Week 5 — Demo REST API with RBAC and role-filtered views.

Run locally:
  cd week09-rbac-api
  python app.py
"""

from flask import Flask, jsonify

from rbac import get_current_user, require_any_permission, require_permission

app = Flask(__name__)

DOCUMENTS = {
    "doc_checking_001": {
        "doc_id": "doc_checking_001",
        "title": "Checking account statement",
        "summary": "Demo checking balance inquiry",
        "account_type": "checking",
        "balance": "$1,847.32",
        "internal_risk_flag": "low",
        "audit_trail_id": "audit_9001",
    }
}

AUDIT_LOGS = [
    {
        "event_id": "evt_001",
        "action": "balance_inquiry",
        "user_id": "user_analyst_01",
        "doc_id": "doc_checking_001",
        "timestamp": "2026-06-30T10:00:00Z",
    },
    {
        "event_id": "evt_002",
        "action": "document_view",
        "user_id": "user_manager_01",
        "doc_id": "doc_checking_001",
        "timestamp": "2026-06-30T11:30:00Z",
    },
]


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/v1/account/balance")
@require_permission("balance:read")
def account_balance():
    user = get_current_user()
    return jsonify(
        {
            "user_id": user["user_id"],
            "role": user["role"],
            "account_type": "checking",
            "balance": "$1,847.32",
        }
    )


@app.get("/api/v1/transfer/limit")
@require_permission("transfer:read")
def transfer_limit():
    return jsonify(
        {
            "account_type": "checking",
            "daily_transfer_limit": "$3,000.00",
        }
    )


@app.get("/api/v1/audit/logs")
@require_permission("audit:read")
def audit_logs():
    return jsonify({"events": AUDIT_LOGS, "count": len(AUDIT_LOGS)})


@app.get("/api/v1/documents/<doc_id>")
@require_any_permission(
    "documents:read_summary",
    "documents:read_full",
    "documents:read_metadata",
)
def document_view(doc_id: str):
    user = get_current_user()
    doc = DOCUMENTS.get(doc_id)
    if not doc:
        return jsonify({"error": "not_found", "doc_id": doc_id}), 404

    role = user["role"]
    if role == "manager":
        return jsonify({k: v for k, v in doc.items()})
    if role == "auditor":
        return jsonify(
            {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "audit_trail_id": doc["audit_trail_id"],
            }
        )
    # analyst — summary view only (no balance, no internal flags)
    return jsonify(
        {
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "summary": doc["summary"],
            "account_type": doc["account_type"],
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
