"""Atomic, reversible writes confined to brutallOS's own onboarding file."""
import json
import os
from pathlib import Path
import tempfile
from contextlib import contextmanager
import fcntl

from catalog import defaults, validate


class Preferences:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / "welcome.json"
        self.backup = self.directory / "welcome.previous.json"

    @contextmanager
    def locked(self):
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (self.directory / ".welcome.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def read(self):
        if not self.path.exists():
            return defaults()
        return validate(json.loads(self.path.read_text(encoding="utf-8")))

    def atomic(self, path, content):
        fd, name = tempfile.mkstemp(prefix=".welcome-", dir=self.directory)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def save(self, data):
        validate(data)
        payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()
        with self.locked():
            # Enclose the original bytes (even an invalid file) and the expected
            # new bytes. Refuse rollback if another writer changed the result.
            old = self.path.read_bytes() if self.path.exists() else None
            snapshot = {"before": old.hex() if old is not None else None,
                        "after": payload.hex()}
            self.atomic(self.backup, json.dumps(snapshot).encode())
            self.atomic(self.path, payload)

    def restore(self):
        with self.locked():
            if not self.backup.exists():
                raise ValueError("Nenhuma gravação disponível para desfazer.")
            snapshot = json.loads(self.backup.read_text())
            expected = bytes.fromhex(snapshot["after"])
            if not self.path.exists() or self.path.read_bytes() != expected:
                raise ValueError("Preferências alteradas desde o backup. Reversão cancelada para preservar as alterações.")
            before = snapshot["before"]
            if before is None:
                self.path.unlink()
            else:
                self.atomic(self.path, bytes.fromhex(before))
            self.backup.unlink()
