"""JSON bridge to public Plasma desktop scripting, without a shell."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def evaluate(script, function, action, options):
    qdbus = shutil.which("qdbus6") or shutil.which("qdbus-qt6") or "/usr/lib/qt6/bin/qdbus"
    code = (ROOT / "plasma/layouts" / script).read_text() + "\nprint(JSON.stringify(" + function + "(" + json.dumps(action) + "," + json.dumps(options) + ")));"
    try:
        result = subprocess.run([qdbus, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", code], capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired as error:
        raise ValueError("Plasma não respondeu. O resultado remoto é desconhecido; mantenha o backup.") from error
    if result.returncode: raise ValueError((result.stderr or result.stdout).strip()[:1500])
    return json.loads(result.stdout)
