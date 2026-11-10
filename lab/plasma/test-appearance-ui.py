"""Exercise the real theme controls, including their asynchronous native process."""
import json
from pathlib import Path
import subprocess
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
from PySide6.QtQuick import QQuickWindow
sys.path.insert(0, "/project/apps/brutall-center")
from main import create_engine

app = QGuiApplication([])
engine, backend = create_engine()
window = engine.rootObjects()[0]
window.setProperty("page", 3)
window.setPosition(400, 140)
QTest.qWait(200)


def find(item, name):
    if item.objectName() == name: return item
    for child in item.childItems():
        found = find(child, name)
        if found is not None: return found


def click(name):
    item = find(window.contentItem(), name)
    assert item is not None and item.isVisible() and item.isEnabled(), name
    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, item.mapToScene(item.boundingRect().center()).toPoint())
    for attempt in range(150):
        QTest.qWait(100)
        if not backend.appearanceBusy: break
    assert not backend.appearanceBusy, backend.message


before = window.property("dark")
click("applyDark")
assert backend.canUndoAppearance and window.property("dark"), backend.message
QTest.qWait(1000)
subprocess.run(["python3", "/project/lab/plasma/capture.py", "/results/bru-dark-settings.png"], check=True)
click("undoAppearance")
assert not backend.canUndoAppearance and window.property("dark") == before, backend.message
QTest.qWait(1000)
subprocess.run(["python3", "/project/lab/plasma/capture.py", "/results/bru-light-settings.png"], check=True)
Path("/results/bru-ui.json").write_text(json.dumps({"applyDarkViaButton": True, "undoViaButton": True}, indent=2))
window.close()
print("PASS: apply dark and undo through the actual QML buttons")
