"""Headless Qt integration: real QML controls, images, persistence and keyboard."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
from pathlib import Path
import sys
import tempfile
import unittest

from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/brutall-welcome"))
from main import create_engine
from catalog import THEMES


class WelcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_full_onboarding(self):
        messages = []
        previous = qInstallMessageHandler(lambda kind, context, message: messages.append(message))
        self.addCleanup(lambda: qInstallMessageHandler(previous))
        with tempfile.TemporaryDirectory() as directory:
            engine, backend = create_engine(self.app, directory)
            self.assertTrue(engine.rootObjects(), messages)
            window = engine.rootObjects()[0]
            window.resize(1080, 1200)
            QTest.qWait(150)
            self.assertFalse((Path(directory) / "welcome.json").exists())

            def find(name):
                # Repeater delegates have visual rather than QObject parents.
                def walk(item):
                    if item.objectName() == name:
                        return item
                    if isinstance(item, QQuickItem):
                        for child in item.childItems():
                            result = walk(child)
                            if result is not None:
                                return result
                result = walk(window.contentItem())
                self.assertIsNotNone(result, name)
                return result

            def click(name):
                item = find(name)
                self.assertTrue(item.isVisible(), name)
                point = item.mapToScene(item.boundingRect().center()).toPoint()
                QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, point)
                QTest.qWait(30)

            # Keyboard activation of the primary navigation button.
            find("nextButton").forceActiveFocus()
            QTest.keyClick(window, Qt.Key_Space)
            self.assertEqual(window.property("step"), 1)
            click("nextButton")
            self.assertEqual(window.property("step"), 2)
            for ti, theme in enumerate(THEMES):
                click("theme" + str(ti))
                for vi, variant in enumerate(theme["variants"]):
                    click("variant" + str(vi))
                    preview = find("wallpaperPreview")
                    QTest.qWait(30)
                    self.assertTrue(preview.property("loaded"), variant["file"])
                    self.assertTrue(preview.property("source").toString().endswith(variant["file"]))
            click("nextButton")
            click("preset1")
            click("nextButton")
            self.assertEqual(window.property("step"), 4)
            click("saveButton")
            self.assertEqual(window.property("step"), 5)
            self.assertEqual(backend.store.read()["theme"], "friends")
            self.assertEqual(backend.store.read()["variant"], "purple")
            self.assertEqual(backend.store.read()["preset"], "developer")

            # Reopen with saved choices, then undo through the actual UI.
            other_engine, other_backend = create_engine(self.app, directory)
            other = other_engine.rootObjects()[0]
            self.assertEqual(other.property("themeIndex"), 2)
            self.assertEqual(other.property("variantIndex"), 2)
            other.close()
            click("restoreButton")
            self.assertFalse(backend.store.path.exists())

            # Render each page in both appearances at the smaller supported size.
            output = ROOT / "docs/screenshots"
            output.mkdir(exist_ok=True)
            for width, height in ((1000, 720), (1366, 768), (1920, 1080)):
                for appearance in ("light", "dark"):
                    window.setProperty("appearance", appearance)
                    window.resize(width, height)
                    for step in range(5):
                        window.setProperty("step", step)
                        QTest.qWait(40)
                        frame = window.grabWindow()
                        self.assertFalse(frame.isNull())
                        if width == 1000 and step in (0, 4) and not os.environ.get("QT_SCALE_FACTOR"):
                            frame.save(str(output / f"welcome-{appearance}-{step}.png"))
            window.close()
            # Engine must die before backend context object.
            del other_engine, engine
            self.app.processEvents()
            errors = [m for m in messages if any(token in m for token in ("Error", "Unable", "failed", "Cannot", "Binding loop"))]
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
