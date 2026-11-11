"""Live X11/Wayland: native Qt palette matches selected identity; exact rollback."""
import base64
import json
from pathlib import Path
import subprocess
import sys


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def verify(accent, window):
    code = "from PySide6.QtGui import QGuiApplication; a=QGuiApplication([]); print(a.palette().highlight().color().name(), a.palette().window().color().name())"
    assert command(sys.executable, "-c", code) == accent + " " + window


script = "/project/scripts/brutall-appearance"
for accent, tinted, window in (("auto", "yes", "#221b3a"), ("#0099bb", "no", "#151827")):
    output = command(script, "apply", "--mode", "dark", "--theme", "friends", "--variant", "purple", "--accent", accent, "--tinted", tinted)
    backup = next(line[8:] for line in output.splitlines() if line.startswith("Backup: "))
    verify("#9333ea" if accent == "auto" else accent, window)
    command(script, "rollback", "--backup", backup)
    manifest = json.loads(Path(backup).read_text())
    for item in manifest["files"]:
        path = Path(item["path"])
        assert (path.read_bytes() if path.exists() else None) == (base64.b64decode(item["before"]) if item["before"] is not None else None), path
print("PASS: new native Qt clients receive automatic/custom accent and tinted/neutral surfaces; exact file rollback")
