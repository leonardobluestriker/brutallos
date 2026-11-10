"""Atomic, conflict-aware backups for project-owned user files."""
import base64
import hashlib
import os
from pathlib import Path
import tempfile

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".bru-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def snapshot(paths):
    if any(path.is_symlink() for path in paths):
        raise ValueError("Há arquivos de tema/configuração gerenciados por links simbólicos. Aplicação recusada para preservar os links.")
    return [{"path": str(path), "before": base64.b64encode(path.read_bytes()).decode() if path.exists() else None,
             "mode": path.stat().st_mode & 0o777 if path.exists() else None} for path in paths]


def restore(files):
    # Check every file before restoring any: do not partially undo on a conflict.
    for item in files:
        if digest(Path(item["path"])) != item["after"]:
            raise ValueError("Arquivo alterado após a aplicação: " + item["path"] + ". Reversão recusada para preservar as alterações.")
    for item in files:
        path = Path(item["path"])
        if item["before"] is None:
            path.unlink(missing_ok=True)
        else:
            atomic(path, base64.b64decode(item["before"]))
            if item.get("mode") is not None: path.chmod(item["mode"])
