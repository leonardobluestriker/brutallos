import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QGuiApplication
from PySide6.QtTest import QTest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/brutall-center"))
from instance import LauncherInstance


class LauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QGuiApplication.instance() or QGuiApplication([])

    def test_installer_restores_previous_entry_and_removes_new_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            entry = data / "applications/org.brutallos.Center.desktop"
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"original\n")
            environment = dict(os.environ, XDG_DATA_HOME=str(data), XDG_STATE_HOME=str(root / "state"))
            command = [sys.executable, str(ROOT / "scripts/brutall-launcher")]
            output = subprocess.check_output(command + ["install"], env=environment, text=True)
            backup = output.splitlines()[0][8:]
            self.assertIn("--launcher", (data / "applications/org.brutallos.Launcher.desktop").read_text())
            subprocess.run(command + ["rollback", "--backup", backup], env=environment, capture_output=True, check=True)
            self.assertEqual(entry.read_bytes(), b"original\n")
            self.assertFalse((data / "applications/org.brutallos.Launcher.desktop").exists())

    def test_second_instance_activates_first_without_another_window(self):
        with tempfile.TemporaryDirectory() as directory:
            name = str(Path(directory) / "test.sock")
            first = LauncherInstance(name)
            self.assertTrue(first.acquire())
            class Window:
                activations = 0
                def showNormal(self): pass
                def raise_(self): pass
                def requestActivate(self): self.activations += 1
            window = Window()
            first.bind(window)
            second = LauncherInstance(name)
            self.assertFalse(second.acquire())
            QTest.qWait(50)
            self.assertEqual(window.activations, 1)
            first.close()
