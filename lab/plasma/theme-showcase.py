"""Capture the live Bru theme in the disposable Plasma laboratory."""
import json
from pathlib import Path
import subprocess
import time


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def capture(name):
    run("xdotool", "mousemove", "5", "5")
    time.sleep(0.3)
    run("python3", "/project/lab/plasma/capture.py", "/results/" + name + ".png")


# Close only read-only prototype windows belonging to this disposable test session.
windows = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", "^Central brutallOS$"], capture_output=True, text=True)
for window in windows.stdout.splitlines():
    subprocess.run(["xdotool", "windowclose", window])

# Recreate only the lab-owned dock, through its real rollback and apply commands,
# so the revised launcher ordering is exercised without resetting unrelated panels.
status = json.loads(run("/project/scripts/brutall-dock", "status"))
if status["existing"]:
    owner = status["existing"][0]["owner"]
    for manifest in (Path.home() / ".local/state/brutallos/dock/backups").glob("*/manifest.json"):
        if json.loads(manifest.read_text())["owner"] == owner:
            run("/project/scripts/brutall-dock", "rollback", "--backup", str(manifest.parent))
            break
run("/project/scripts/brutall-dock", "apply")
run("/usr/lib/qt6/bin/qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript",
    "var ps=panels();for(var i=0;i<ps.length;i++){ps[i].currentConfigGroup=['General'];if(ps[i].readConfig('brutallOSRole','')==='brutallos-top-v1')ps[i].height=32;}print('compact top');")

for mode in ("light", "dark"):
    run("/project/scripts/brutall-appearance", "apply", "--mode", mode)
    time.sleep(1)
    for page, name in [(0, "launcher"), (2, "striker"), (3, "appearance")]:
        with open("/results/bru-" + mode + "-" + name + ".log", "w") as log:
            process = subprocess.Popen(["python3", "/project/lab/plasma/launch-app.py", "center", str(page)], stdout=log, stderr=log)
            time.sleep(3)
            assert process.poll() is None
            capture("bru-" + mode + "-" + name)
            process.terminate()
            process.wait(timeout=10)
print("PASS: six full-desktop Bru captures, light and dark")
