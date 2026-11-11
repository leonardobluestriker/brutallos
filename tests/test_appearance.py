import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import sys
import unittest
import json
import os
from contextlib import redirect_stdout
import io
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
loader = importlib.machinery.SourceFileLoader("appearance", str(ROOT / "scripts/brutall-appearance"))
spec = importlib.util.spec_from_loader(loader.name, loader)
appearance = importlib.util.module_from_spec(spec)
loader.exec_module(appearance)


class AppearanceTests(unittest.TestCase):
    def test_rollback_accepts_legacy_and_extended_backup_destinations(self):
        for version in (1, 2):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                config, data = root / "config", root / "data"
                config.mkdir()
                old = config / "kwinrc"
                old.write_bytes(b"previous settings\n")
                _, paths = appearance.destinations(config, data)
                if version == 2:
                    paths += [config / "brutallos/interface.json", data / "color-schemes/BrutallIdentity.colors"]
                files = appearance.snapshot(paths)
                old.write_bytes(b"applied settings\n")
                for item in files: item["after"] = appearance.digest(Path(item["path"]))
                backup = root / "backup.json"
                backup.write_text(json.dumps(dict(schemaVersion=version, files=files)))
                environment = dict(XDG_CONFIG_HOME=str(config), XDG_DATA_HOME=str(data), XDG_STATE_HOME=str(root / "state"))
                def native(*args):
                    return "KWin version: 6.3.6" if args[-1] == "org.kde.KWin.supportInformation" else ""
                with patch.dict(os.environ, environment), patch.object(sys, "argv", ["brutall-appearance", "rollback", "--backup", str(backup)]), \
                     patch.object(appearance.shutil, "which", return_value=sys.executable), patch.object(appearance, "native", side_effect=native), redirect_stdout(io.StringIO()):
                    self.assertEqual(appearance.main(), 0)
                self.assertEqual(old.read_bytes(), b"previous settings\n")

    def test_restore_exact_bytes_and_remove_new_files(self):
        with tempfile.TemporaryDirectory() as directory:
            old, new = Path(directory) / "old", Path(directory) / "new"
            old.write_bytes(b"original\n")
            old.chmod(0o640)
            files = appearance.snapshot([old, new])
            appearance.atomic(old, b"changed")
            appearance.atomic(new, b"new")
            for item in files: item["after"] = appearance.digest(Path(item["path"]))
            appearance.restore(files)
            self.assertEqual(old.read_bytes(), b"original\n")
            self.assertEqual(old.stat().st_mode & 0o777, 0o640)
            self.assertFalse(new.exists())

    def test_conflict_blocks_every_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            a.write_bytes(b"old a"); b.write_bytes(b"old b")
            files = appearance.snapshot([a, b])
            a.write_bytes(b"new a"); b.write_bytes(b"new b")
            for item in files: item["after"] = appearance.digest(Path(item["path"]))
            b.write_bytes(b"external change")
            with self.assertRaisesRegex(ValueError, "alterado"):
                appearance.restore(files)
            self.assertEqual(a.read_bytes(), b"new a")
            self.assertEqual(b.read_bytes(), b"external change")
