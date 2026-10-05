"""Mirror of fleet-worker validate_host_local allowlist."""
from __future__ import annotations

ALLOWED = {
    "operation": "yarn-degradation-curve",
    "host": "f6a8",
    "seat": "hyperqwen",
    "artifact_root": "/home/odnt/RND/uow7-inference-recipe-rollout",
}
TIMEOUT_MIN = 1
TIMEOUT_MAX = 1200
FORBIDDEN_KEYS = ("command", "image", "task")


def validate_request(body: dict) -> int:
    if not isinstance(body, dict):
        raise ValueError("body must be a JSON object")
    for k in FORBIDDEN_KEYS:
        if k in body and body[k] not in (None, "", [], {}):
            raise ValueError(f"host-local execution rejects {k}")
    for k, v in ALLOWED.items():
        if body.get(k) != v:
            raise ValueError(f"{k} must be {v!r}, got {body.get(k)!r}")
    timeout = body.get("request_timeout_seconds")
    if not isinstance(timeout, int):
        raise ValueError("request_timeout_seconds is required int")
    if not (TIMEOUT_MIN <= timeout <= TIMEOUT_MAX):
        raise ValueError(f"request timeout must be between {TIMEOUT_MIN} and {TIMEOUT_MAX}")
    return timeout
