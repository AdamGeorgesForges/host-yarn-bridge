from __future__ import annotations
import os, json, tempfile
from pathlib import Path


def safe_join(root: str, *parts: str) -> Path:
    base = Path(root).resolve()
    target = (base.joinpath(*parts)).resolve()
    if not str(target).startswith(str(base) + os.sep) and target != base:
        raise ValueError("artifact path escapes root")
    if target.exists() and (target.is_symlink() or not target.is_file() and not target.is_dir()):
        # reject symlink escape / special files when present
        if target.is_symlink():
            raise ValueError("symlink artifact rejected")
    return target


def atomic_write(path: Path, data: str | bytes, mode: str = "w") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "wb":
        raw = data if isinstance(data, (bytes, bytearray)) else data.encode()
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(raw)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                try: os.unlink(tmp)
                except OSError: pass
    else:
        text = data if isinstance(data, str) else data.decode()
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", text=True)
        try:
            with os.fdopen(fd, "w") as f:
                f.write(text)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                try: os.unlink(tmp)
                except OSError: pass


def write_json(path: Path, obj) -> None:
    atomic_write(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")
