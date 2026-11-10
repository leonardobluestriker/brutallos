"""Full-desktop photos of the live lab, without image editing or compositing."""
import json
import os
from pathlib import Path
import subprocess
import time

OUTPUT = Path("/results")


def wallpaper(filename):
    code = "var ds=desktops();for(var i=0;i<ds.length;i++){ds[i].wallpaperPlugin='org.kde.image';ds[i].currentConfigGroup=['Wallpaper','org.kde.image','General'];ds[i].writeConfig('Image'," + json.dumps("file:///project/assets/wallpapers/" + filename) + ");}print('set');"
    subprocess.run(["/usr/lib/qt6/bin/qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", code], check=True)
    time.sleep(2)


def capture(name):
    subprocess.run(["xdotool", "mousemove", "5", "5"], check=True)
    time.sleep(0.3)
    environment = dict(os.environ, QT_QPA_PLATFORM="xcb")
    subprocess.run(["python3", "/project/lab/plasma/capture.py", str(OUTPUT / name)], env=environment, check=True)


wallpaper("BRU1.png")
capture("01-desktop-bru.png")
for name, kind, page in [("02-launcher.png", "center", "0"), ("03-striker.png", "center", "2"),
                         ("04-welcome-friends.png", "welcome", "2")]:
    if kind == "welcome":
        wallpaper("BLUESTRIKER.png")
    with (OUTPUT / (name + ".log")).open("w") as log:
        process = subprocess.Popen(["python3", "/project/lab/plasma/launch-app.py", kind, page], stdout=log, stderr=log)
        time.sleep(3)
        assert process.poll() is None, "Application exited; inspect its log"
        capture(name)
        process.terminate()
        process.wait(timeout=10)
wallpaper("RAIO1.png")
capture("08-desktop-raio.png")
wallpaper("BRU1.png")
