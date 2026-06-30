"""Simple RBAC helpers for the demo API."""

import json
from functools import wraps
from pathlib import Path

from flask import jsonify, request

ROOT = Path(__file__).resolve().parent.parent
USERS_FILE = ROOT / "data" / "rbac_users.json"

ROLE_PERMISSIONS = {
    "analyst": {"balance:read", "documents:read_summary"},
    "manager": {"balance:read", "documents:read_full", "transfer:read", "audit:read"},
    "auditor": {"audit:read", "documents:read_metadata"},
    "guest": set(),
}


def load_users() -> dict[str, dict]:
    with open(USERS_FILE, encoding="utf-8") as f:
        users = json.load(f)
    return {u["token"]: u for u in users}


def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ").strip()
    return load_users().get(token)


def require_any_permission(*permissions: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({"error": "unauthorized", "message": "Missing or invalid token"}), 401
            role_perms = ROLE_PERMISSIONS.get(user["role"], set())
            if not any(p in role_perms for p in permissions):
                return jsonify(
                    {
                        "error": "forbidden",
                        "message": f"Role '{user['role']}' lacks required permissions",
                        "role": user["role"],
                    }
                ), 403
            request.user = user  # type: ignore[attr-defined]
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def require_permission(permission: str):
    return require_any_permission(permission)
