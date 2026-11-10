"""Live Plasma test: per-screen and all-screen wallpaper changes with rollback."""
import json
from pathlib import Path
import subprocess


def command(*args):
    return subprocess.check_output(["/project/scripts/brutall-wallpaper", *args], text=True)


def status():
    return json.loads(command("status"))


def backup(output):
    return next(line[8:] for line in output.splitlines() if line.startswith("Backup: "))


initial = status()
assert initial["screens"] == 2, "Execute no laboratório com duas saídas."
all_screens = command("apply", "--image", "PURPLELUNA.png", "--all-screens")
assert all(t["image"].endswith("PURPLELUNA.png") for t in status()["targets"])
command("rollback", "--backup", backup(all_screens))
assert status()["targets"] == initial["targets"]
one_screen = command("apply", "--image", "BLUESTRIKER.png", "--screen", "1")
current = status()
assert current["targets"][0] == initial["targets"][0]
assert current["targets"][1]["image"].endswith("BLUESTRIKER.png")
command("rollback", "--backup", backup(one_screen))
assert status()["targets"] == initial["targets"]
Path("/results/wallpaper-multiscreen.json").write_text(json.dumps({
    "initial": initial, "allScreensApplyUndo": True,
    "secondScreenApplyUndoPreservesFirst": True,
}, indent=2))
print("PASS: all-monitors apply and rollback; screen 1 leaves screen 0 untouched")
