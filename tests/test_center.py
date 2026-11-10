import importlib.util
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/brutall-center"))
from services import Metrics, applications
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt
from PySide6.QtQuick import QQuickItem
from PySide6.QtTest import QTest
spec = importlib.util.spec_from_file_location("center_main", ROOT / "apps/brutall-center/main.py")
center = importlib.util.module_from_spec(spec)
spec.loader.exec_module(center)


class ServiceTests(unittest.TestCase):
    def test_hidden_user_override_masks_system_app_and_nested_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("user", "system"):
                (root / name / "applications/sub").mkdir(parents=True)
            (root / "system/applications/a.desktop").write_text("[Desktop Entry]\nType=Application\nName=Visible\nExec=true\n")
            (root / "user/applications/a.desktop").write_text("[Desktop Entry]\nHidden=true\n")
            (root / "system/applications/sub/b.desktop").write_text("[Desktop Entry]\nType=Application\nName=Nested\nExec=true\n")
            result = applications([root / "user", root / "system"])
            self.assertEqual([item["id"] for item in result], ["sub-b.desktop"])

    def test_metrics_delta_and_absent_hardware(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "net").mkdir()
            (root / "stat").write_text("cpu 100 0 100 800 0 0 0 0\n")
            (root / "meminfo").write_text("MemTotal: 2097152 kB\nMemAvailable: 1048576 kB\n")
            (root / "net/dev").write_text("head\nhead\neth0: 100 0 0 0 0 0 0 0 100 0\n")
            reader = Metrics(proc=root, sys=root, disk=root)
            self.assertEqual(reader.sample()["cpu"], "Aguardando amostra")
            (root / "stat").write_text("cpu 150 0 100 850 0 0 0 0\n")
            result = reader.sample()
            self.assertEqual(result["cpu"], "50%")
            self.assertEqual(result["ram"], "1.0 / 2.0 GiB")
            self.assertEqual(result["gpu"], "Indisponível")
            self.assertEqual(result["temperatures"], [])

    def test_unreadable_proc_does_not_invent_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            result = Metrics(Path(directory), Path(directory), Path(directory)).sample()
            self.assertEqual(result["cpu"], "Indisponível")
            self.assertEqual(result["ram"], "Indisponível")


class CenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_category_and_query_are_combined(self):
        entries = [dict(id="a.desktop", name="Editor A", description="", categories="Graphics;", icon=""),
                   dict(id="b.desktop", name="Tool B", description="", categories="Utility;", icon="")]
        with patch.object(center, "applications", return_value=entries):
            backend = center.Center()
        backend.setCategory("Graphics")
        self.assertEqual([item["id"] for item in backend.apps], ["a.desktop"])
        backend.search("Tool")
        self.assertEqual(backend.apps, [])
        backend.setCategory("")
        self.assertEqual([item["id"] for item in backend.apps], ["b.desktop"])

    def test_systemsettings_fallback_discovers_and_opens_only_known_modules(self):
        with patch.object(center.shutil, "which", side_effect=lambda name: "/mock/systemsettings" if name == "systemsettings" else None), \
             patch.object(center.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "kcm_keyboard - Keyboard\nkcm_clock - Date and Time\n", "")):
            backend = center.Center()
        self.assertEqual(backend.settingsCommand, "/mock/systemsettings")
        self.assertTrue(next(item for item in backend.settings if item["module"] == "kcm_keyboard")["available"])
        with patch.object(backend, "start") as start:
            backend.openSettings("kcm_keyboard")
            start.assert_called_once_with("/mock/systemsettings", ["kcm_keyboard"])
            backend.openSettings("untrusted-module")
            self.assertEqual(start.call_count, 1)

    def test_real_qml_pages_keyboard_search_and_monitor_pause(self):
        engine, backend = center.create_engine()
        self.assertTrue(engine.rootObjects())
        window = engine.rootObjects()[0]
        def find(item, name):
            if item.objectName() == name:
                return item
            for child in item.childItems():
                result = find(child, name)
                if result is not None:
                    return result
        QTest.qWait(100)
        search = find(window.contentItem(), "appSearch")
        search.forceActiveFocus()
        search.setProperty("text", "__no_such_app__")
        self.assertEqual(backend.apps, [])
        search.setProperty("text", "")
        self.assertFalse(backend.timer.isActive())
        output = ROOT / "docs/screenshots"
        for page in range(4):
            navigation = find(window.contentItem(), "nav" + str(page))
            navigation.forceActiveFocus()
            QTest.keyClick(window, Qt.Key_Space)
            QTest.qWait(50)
            self.assertEqual(window.property("page"), page)
            self.assertEqual(backend.timer.isActive(), page == 2)
            for dark in (True, False):
                window.setProperty("dark", dark)
                QTest.qWait(30)
                frame = window.grabWindow()
                self.assertFalse(frame.isNull())
                if dark and page in (0, 2):
                    frame.save(str(output / ("center-launcher.png" if page == 0 else "center-striker.png")))
        # Unrecognized identifiers cannot become shell commands or module launches.
        with patch.object(backend, "start") as start:
            backend.launch(";rm -rf /;")
            backend.openSettings("unknown_module")
            start.assert_not_called()
        window.close()
        del engine
