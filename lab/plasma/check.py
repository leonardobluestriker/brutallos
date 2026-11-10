"""Integration checks in a DISPOSABLE Plasma lab, never on a personal desktop."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time

ROOT = Path("/project")
OUTPUT = Path("/results")
QDBUS = "/usr/lib/qt6/bin/qdbus"
results = []


def run(*arguments):
    result = subprocess.run(arguments, text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:] or result.stdout[-3000:])
    return result.stdout.strip()


def evaluate(code):
    return run(QDBUS, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", code)


def command(script, action, *extra):
    return json.loads(run(str(ROOT / "scripts" / script), action, *extra))


def record(name, details):
    results.append(dict(test=name, details=details))
    (OUTPUT / "integration.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(name + ": " + json.dumps(details, ensure_ascii=False), flush=True)


record("versions", {"plasma": run("plasmashell", "--version"), "kwin": run("kwin_x11", "--version"),
                    "session": "X11 / Xvfb / software rendering"})
with tarfile.open(OUTPUT / "baseline-config.tar.gz", "w:gz") as archive:
    archive.add(Path.home() / ".config", arcname=".config")
record("baseline-backup", "baseline-config.tar.gz")
baseline = command("brutall-dock", "plan")
record("initial-dock-plan", baseline)

# Laboratory fixture only: clear the disposable distro's stock panels after
# archiving its config. The product's apply command never removes these panels.
evaluate("var p = panels(); for (var i=0;i<p.length;i++) p[i].remove(); print('lab-fixture-cleared');")
time.sleep(2)
top = command("brutall-top-panel", "apply")
dock = command("brutall-dock", "apply")
assert top["state"] == dock["state"] == "created"
record("apply-both", {"top": top, "dock": dock})
assert command("brutall-top-panel", "apply")["state"] == "unchanged"
assert command("brutall-dock", "apply")["state"] == "unchanged"
record("idempotence", "no duplicate panels")

assert command("brutall-dock", "rollback", "--backup", dock["backup"])["state"] == "removed"
assert len(command("brutall-top-panel", "status")["existing"]) == 1
assert not command("brutall-dock", "status")["existing"]
assert command("brutall-dock", "rollback", "--backup", dock["backup"])["state"] == "absent"
assert command("brutall-top-panel", "rollback", "--backup", top["backup"])["state"] == "removed"
record("selective-rollback", "dock and top removed separately; repeated rollback is absent")
top = command("brutall-top-panel", "apply")
dock = command("brutall-dock", "apply")
time.sleep(3)
run(QDBUS, "org.kde.plasmashell", "/MainApplication", "org.qtproject.Qt.QCoreApplication.quit")
time.sleep(2)
log = (OUTPUT / "plasmashell-restart.log").open("w")
subprocess.Popen(["plasmashell", "--no-respawn"], stdout=log, stderr=subprocess.STDOUT)
for attempt in range(40):
    try:
        after = command("brutall-top-panel", "status")
        if after["existing"]:
            break
    except (RuntimeError, ValueError):
        pass
    time.sleep(0.5)
else:
    raise RuntimeError("Plasma did not restart")
assert after["existing"][0]["id"] == top["id"]
assert command("brutall-dock", "status")["existing"][0]["id"] == dock["id"]
record("shell-restart-persistence", {"topId": top["id"], "dockId": dock["id"]})

wallpaper = str(ROOT / "assets/wallpapers/BRU1.png")
evaluate("var ds=desktops(); for(var i=0;i<ds.length;i++){ds[i].wallpaperPlugin='org.kde.image';ds[i].currentConfigGroup=['Wallpaper','org.kde.image','General'];ds[i].writeConfig('Image'," + json.dumps("file://" + wallpaper) + ");} print('wallpaper-set');")
record("wallpaper", "original BRU1.png, no edits")
try:
    record("lab-colors", run("plasma-apply-colorscheme", "BreezeDark"))
    record("lab-plasma-style", run("plasma-apply-desktoptheme", "breeze-dark"))
except RuntimeError as error:
    record("lab-colors", str(error))
time.sleep(3)
run("python3", str(ROOT / "lab/plasma/capture.py"), str(OUTPUT / "01-desktop-bru.png"))
for name, kind, page in [("02-launcher", "center", "0"), ("03-striker", "center", "2"), ("04-welcome-friends", "welcome", "2")]:
    app_log = (OUTPUT / (name + ".log")).open("w")
    process = subprocess.Popen(["python3", str(ROOT / "lab/plasma/launch-app.py"), kind, page], stdout=app_log, stderr=subprocess.STDOUT)
    time.sleep(4)
    assert process.poll() is None, (OUTPUT / (name + ".log")).read_text()
    run("python3", str(ROOT / "lab/plasma/capture.py"), str(OUTPUT / (name + ".png")))
    process.terminate()
    process.wait(timeout=10)
record("full-screen-captures", "4 screenshots; 1920x1080 root screen")
