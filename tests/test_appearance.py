import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("appearance", str(ROOT / "scripts/brutall-appearance"))
spec = importlib.util.spec_from_loader(loader.name, loader)
appearance = importlib.util.module_from_spec(spec)
loader.exec_module(appearance)


class AppearanceTests(unittest.TestCase):
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
