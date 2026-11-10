"""Exercise all nine original previews and apply/undo through the live central."""
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


def status(): return json.loads(subprocess.check_output(["/project/scripts/brutall-wallpaper", "status"], text=True))


app = QGuiApplication([])
engine, backend = create_engine()
window = engine.rootObjects()[0]
window.resize(1120, 880)
window.setPosition(400, 100)
before = status()
window.setProperty("page", 3)


def wait():
    for attempt in range(150):
        QTest.qWait(100)
        if not backend.wallpaperBusy: return
    raise RuntimeError(backend.message)


def find(item, name):
    if item.objectName() == name: return item
    for child in item.childItems():
        found = find(child, name)
        if found is not None: return found


def click(name, scroll):
    QMetaObject.invokeMethod(window, scroll)
    QTest.qWait(150)
    item = find(window.contentItem(), name)
    assert item is not None and item.isVisible() and item.isEnabled(), name
    point = item.mapToScene(item.boundingRect().center()).toPoint()
    assert 0 < point.y() < window.height() and 0 < point.x() < window.width(), (name, point)
    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
    QTest.qWait(50)


wait()
for theme in range(3):
    click("wallpaperTheme" + str(theme), "showWallpaperThemes")
    assert window.property("themeIndex") == theme
    for variant in range(3):
        click("wallpaperVariant" + str(variant), "showWallpaperActions")
        assert window.property("variantIndex") == variant
        QTest.qWait(50)
        assert find(window.contentItem(), "wallpaperPreview").property("loaded")
click("applyWallpaper", "showWallpaperActions")
wait()
assert backend.canUndoWallpaper, backend.message
assert status()["targets"][0]["image"].endswith("PURPLELUNA.png")
QTest.qWait(2000)
subprocess.run(["xdotool","mousemove","5","5"], check=True)
subprocess.run(["python3","/project/lab/plasma/capture.py","/results/wallpaper-purple-central.png"], check=True)
click("undoWallpaper", "showWallpaperActions")
wait()
assert status()["targets"] == before["targets"], backend.message
window.close()
print("PASS: nine original previews; apply Purple Luna and undo through QML")
