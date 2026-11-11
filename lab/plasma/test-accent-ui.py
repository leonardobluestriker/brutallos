"""Disposable X11 Plasma: live theme preview, native colors, persistence and undo."""
import configparser
import json
from pathlib import Path
import subprocess
import sys
from PySide6.QtCore import Qt, QMetaObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

sys.path.insert(0, "/project/apps/brutall-center")
from main import create_engine


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def backup(output):
    return next(line[8:] for line in output.splitlines() if line.startswith("Backup: "))


def find(item, name):
    if item.objectName() == name: return item
    for child in item.childItems():
        result = find(child, name)
        if result is not None: return result


app = QGuiApplication([])
engine, backend = create_engine()
window = engine.rootObjects()[0]
window.resize(1120, 920)
window.setPosition(400, 100)
window.setProperty("page", 3)


def wait():
    for attempt in range(160):
        QTest.qWait(100)
        if not backend.appearanceBusy and not backend.wallpaperBusy: return
    raise RuntimeError(backend.message)


def click(name, scroll="showWallpaperActions"):
    QMetaObject.invokeMethod(window, scroll)
    QTest.qWait(150)
    item = find(window.contentItem(), name)
    assert item is not None and item.isEnabled(), (name, backend.message)
    point = item.mapToScene(item.boundingRect().center()).toPoint()
    assert 0 < point.x() < window.width() and 0 < point.y() < window.height(), (name, point)
    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
    QTest.qWait(100)


def native_colors():
    config = configparser.ConfigParser()
    config.read(Path.home() / ".config/kdeglobals")
    return config


def capture(name):
    QMetaObject.invokeMethod(window, "showWallpaperThemes")
    QTest.qWait(1000)
    command("xdotool", "mousemove", "5", "5")
    command("python3", "/project/lab/plasma/capture.py", "/results/" + name + ".png")


wait()
click("wallpaperTheme2", "showWallpaperThemes")
click("wallpaperVariant2")
click("automaticAccent")
assert window.property("accent").name() == "#9333ea"
tinted_paper = window.property("paper").name()
if window.property("tinted"):
    click("tintedSurfaces")
assert window.property("paper").name() != tinted_paper
click("tintedSurfaces")
field = find(window.contentItem(), "accentInput")
field.setProperty("text", "#invalid")
assert not field.property("acceptableInput")
assert not find(window.contentItem(), "applyDark").isEnabled()
field.setProperty("text", "#09b")
field.forceActiveFocus()
QTest.keyClick(window, Qt.Key_Return)
assert window.property("accent").name() == "#0099bb"
click("automaticAccent")
click("applyDark")
wait()
assert backend.canUndoAppearance, backend.message
first_backup = backend._appearanceBackup
config = native_colors()
assert config["Colors:Selection"]["BackgroundNormal"] == "147,51,234", dict(config["Colors:Selection"])
assert config["Colors:Window"]["BackgroundNormal"] == "34,27,58"
saved = Path.home() / ".config/brutallos/interface.json"
assert json.loads(saved.read_text())["variant"] == "purple"
wallpaper_backup = backup(command("/project/scripts/brutall-wallpaper", "apply", "--image", "PURPLELUNA.png"))
capture("luna-interface-dark")

# Reopening the dedicated launcher reads the saved identity and mode.
window.hide()
launcher = subprocess.Popen([sys.executable, "/project/apps/brutall-center/main.py", "--launcher"])
QTest.qWait(2500)
ids = command("xdotool", "search", "--onlyvisible", "--name", "^Aplicativos brutallOS$").splitlines()
assert len(ids) == 1
command("xdotool", "windowmove", ids[0], "438", "200")
command("xdotool", "windowactivate", "--sync", ids[0])
QTest.qWait(500)
command("python3", "/project/lab/plasma/capture.py", "/results/luna-launcher-dark.png")
command("xdotool", "key", "Escape")
launcher.wait(timeout=5)
assert launcher.returncode == 0
window.showNormal()
window.requestActivate()

# Same named scheme must reload when its custom accent changes.
backend.applyAppearance("dark", "friends", "purple", "#0099bb", False)
wait()
assert native_colors()["Colors:Selection"]["BackgroundNormal"] == "0,153,187"
assert native_colors()["Colors:Window"]["BackgroundNormal"] == "21,24,39"
assert json.loads(saved.read_text())["accent"] == "#0099bb"
backend.undoAppearance()
wait()
assert json.loads(saved.read_text())["accent"] is None
assert window.property("accent").name() == "#9333ea"
backend.applyAppearance("light", "friends", "purple", "auto", True)
wait()
capture("luna-interface-light")
backend.undoAppearance()
wait()
assert json.loads(saved.read_text())["mode"] == "dark"
window.close()
command("/project/scripts/brutall-wallpaper", "rollback", "--backup", wallpaper_backup)
command("/project/scripts/brutall-appearance", "rollback", "--backup", first_backup)
manifest = json.loads(Path(first_backup).read_text())
import base64
for item in manifest["files"]:
    path = Path(item["path"])
    assert (path.read_bytes() if path.exists() else None) == (base64.b64decode(item["before"]) if item["before"] is not None else None), path
print("PASS: automatic Luna preview; tinted/neutral surfaces; HEX validation; native KDE colors; saved launcher identity; repeated custom color apply; light/dark; exact file rollback")
