import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/brutall-welcome"))
from catalog import THEMES


class AssetTests(unittest.TestCase):
    def test_exact_original_images(self):
        directory = ROOT / "assets/wallpapers"
        manifest = {}
        for line in (directory / "SHA256SUMS").read_text().splitlines():
            digest, filename = line.split()
            manifest[filename] = digest
            self.assertEqual(hashlib.sha256((directory / filename).read_bytes()).hexdigest(), digest, filename)
        self.assertEqual(set(manifest), {v["file"] for t in THEMES for v in t["variants"]})


if __name__ == "__main__":
    unittest.main()
