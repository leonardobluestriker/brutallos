"""Real Plasma: reversible wallpapers and native dock-to-launcher opening."""
import json
from pathlib import Path
import subprocess
import time

ROOT = Path("/project")


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode: raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def wallpaper(action, *args):
    return run(str(ROOT / "scripts/brutall-wallpaper"), action, *args)


def backup(output): return output.splitlines()[0][8:]


initial = json.loads(wallpaper("status"))
reports = {"initial": initial, "nineOriginals": []}
files = sorted(path.name for path in (ROOT / "assets/wallpapers").glob("*.png"))
for name in files:
    result = wallpaper("apply", "--image", name)
    after = json.loads(wallpaper("status"))
    assert after["targets"][0]["image"].endswith(name)
    wallpaper("rollback", "--backup", backup(result))
    assert json.loads(wallpaper("status"))["targets"][0]["image"] == initial["targets"][0]["image"]
    reports["nineOriginals"].append(name)

script = str(ROOT / "scripts/brutall-launcher")
# The lab currently has the connected launcher; restore it using its own backup.
records = sorted((Path.home() / ".local/state/brutallos/launcher").glob("*.json"), key=lambda p:p.stat().st_mtime, reverse=True)
for path in records:
    if json.loads(path.read_text()).get("kind") == "connection":
        try: run(script, "rollback", "--backup", str(path)); break
        except RuntimeError: pass
before_code = "var p=panels().filter(function(p){return p.location==='bottom'})[0];print(JSON.stringify(p.widgets('org.kde.plasma.icontasks').map(function(w){w.currentConfigGroup=['General'];return {id:w.id,favorites:w.readConfig('launchers',[])};})));"
def tasks(): return json.loads(run("/usr/lib/qt6/bin/qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", before_code))
original_tasks = tasks()
connection = run(script, "connect")
assert tasks() == original_tasks
assert "já conectado" in run(script, "connect")
run(script, "rollback", "--backup", backup(connection))
assert tasks() == original_tasks
run(script, "connect")
reports["taskManagerAndFavoritesPreserved"] = True

# Close old lab launcher windows, then click the actual native dock applet.
existing = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", "^Aplicativos brutallOS$"], capture_output=True, text=True)
for window in existing.stdout.splitlines(): subprocess.run(["xdotool", "windowclose", window])
time.sleep(0.5)
ids = run("xdotool", "search", "--onlyvisible", "--class", "plasmashell").splitlines()
for window in ids:
    geo = dict(line.split("=",1) for line in run("xdotool", "getwindowgeometry", "--shell", window).splitlines())
    if int(geo["Y"]) > 900 and int(geo["WIDTH"]) < 1000:
        dock_point = [str(int(geo["X"])+int(geo["WIDTH"])-32), str(int(geo["Y"])+int(geo["HEIGHT"])//2)]
        run("xdotool", "mousemove", *dock_point, "click", "1")
        break
else: raise RuntimeError("Dock não encontrada")
time.sleep(3)
windows = run("xdotool", "search", "--onlyvisible", "--name", "^Aplicativos brutallOS$").splitlines()
assert len(windows)==1
run("python3", str(ROOT / "apps/brutall-center/main.py"), "--launcher")
assert run("xdotool", "search", "--onlyvisible", "--name", "^Aplicativos brutallOS$").splitlines()==windows
reports["dockOpensOwnLauncher"] = True
reports["singleInstance"] = True
run("xdotool", "windowactivate", "--sync", windows[0])
run("xdotool", "key", "Escape")
time.sleep(0.5)
assert subprocess.run(["xdotool","search","--onlyvisible","--name","^Aplicativos brutallOS$"], capture_output=True).returncode != 0
reports["escapeCloses"] = True
run("xdotool", "mousemove", *dock_point, "click", "1")
time.sleep(3)
window = run("xdotool", "search", "--onlyvisible", "--name", "^Aplicativos brutallOS$").splitlines()[0]
run("xdotool", "windowactivate", "--sync", window)
run("xdotool", "type", "--clearmodifiers", "Dolphin")
run("xdotool", "key", "Return")
time.sleep(2)
assert subprocess.run(["xdotool","search","--onlyvisible","--name","^Aplicativos brutallOS$"], capture_output=True).returncode != 0
assert run("xdotool", "search", "--onlyvisible", "--class", "dolphin")
assert subprocess.run(["pgrep", "-f", "^/usr/bin/python3 /project/apps/brutall-center/main.py --launcher$"], capture_output=True).returncode != 0
reports["enterLaunchesDolphinAndExitsLauncher"] = True
Path("/results/launcher-wallpaper-tests.json").write_text(json.dumps(reports, indent=2))
print("PASS: nine wallpapers/undo; dock linkage/undo; favorites; one instance; Escape; Enter opens Dolphin and releases launcher process")
