"""Click the rendered KWin decoration and verify actual native window states."""
import json
from pathlib import Path
import subprocess
import time


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def state(window):
    return run("xprop", "-id", window, "_NET_WM_STATE")


def geometry(window):
    return {key: int(value) for key, value in (line.split("=", 1) for line in run("xdotool", "getwindowgeometry", "--shell", window).splitlines())}


def click(window, offset):
    geometry = dict(line.split("=", 1) for line in run("xdotool", "getwindowgeometry", "--shell", window).splitlines())
    x, y = int(geometry["X"]) + offset, int(geometry["Y"]) - 19
    run("xdotool", "mousemove", str(x), str(y), "click", "1")
    time.sleep(0.6)


log = Path("/results/bru-controls-app.log").open("w")
process = subprocess.Popen(["python3", "/project/lab/plasma/launch-app.py", "center", "2"], stdout=log, stderr=log)
time.sleep(3)
window = run("xdotool", "search", "--onlyvisible", "--pid", str(process.pid)).splitlines()[0]
run("xdotool", "windowactivate", "--sync", window)
run("python3", "/project/lab/plasma/capture.py", "/results/bru-controls-before.png")
click(window, 79)
assert "MAXIMIZED_VERT" in state(window), state(window)
click(window, 79)
assert "MAXIMIZED_VERT" not in state(window), state(window)
before = geometry(window)
run("xdotool", "mousemove", str(before["X"] + before["WIDTH"] // 2), str(before["Y"] - 19),
    "mousedown", "1", "mousemove_relative", "--sync", "70", "30", "mouseup", "1")
time.sleep(0.6)
assert geometry(window)["X"] != before["X"], "Native title drag did not move the window"
run("xdotool", "windowsize", window, "1000", "680")
time.sleep(0.6)
assert geometry(window)["WIDTH"] == 1000
click(window, 51)
assert "HIDDEN" in state(window), state(window)
run("xdotool", "windowmap", window)
run("xdotool", "windowactivate", "--sync", window)
time.sleep(0.6)
click(window, 23)
process.wait(timeout=5)
assert process.returncode == 0
Path("/results/bru-controls.json").write_text(json.dumps({"greenMaximize": True, "greenRestore": True,
    "yellowMinimize": True, "redClose": True, "nativeTitleDrag": True, "resize": True, "windowId": window}, indent=2))
print("PASS: green maximizes/restores, yellow minimizes, red closes; native title drag and resize")
