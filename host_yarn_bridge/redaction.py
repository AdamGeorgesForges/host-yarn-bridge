from __future__ import annotations
import re

PATTERNS = [
    (re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"), r"\1***"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "ghp_***"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "github_pat_***"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "sk-***"),
    (re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[=:]\s*\S+"), r"\1=***"),
    (re.compile(r"https?://[^\s/@]+:[^\s/@]+@"), "https://***:***@"),
]


def redact(text: str) -> tuple[str, int]:
    n = 0
    out = text
    for rx, repl in PATTERNS:
        out, c = rx.subn(repl, out)
        n += c
    return out, n
