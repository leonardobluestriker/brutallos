import json
import os
from pathlib import Path
import unittest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QJSEngine

ROOT = Path(__file__).resolve().parents[1]


class WallpaperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QGuiApplication.instance() or QGuiApplication([])

    def setUp(self):
        self.js = QJSEngine()
        self.js.evaluate('''var locked=false;var screenCount=2;
        var ds=[0,1].map(function(i){return {id:i+1,screen:i,wallpaperPlugin:i===0?"org.kde.slideshow":"org.kde.image",currentConfigGroup:[],image:"old"+i,unrelated:17,
        readConfig:function(k,f){return this.image;},writeConfig:function(k,v){this.image=v;}};});
        function desktopForScreen(i){return ds[i];}
        function desktopById(id){return ds.filter(function(d){return d.id===id;})[0];}''')
        self.js.evaluate((ROOT / "plasma/layouts/wallpaper.js").read_text())

    def value(self, text):
        value = self.js.evaluate("JSON.stringify(" + text + ")")
        self.assertFalse(value.isError(), value.toString())
        return json.loads(value.toString())

    def transaction(self):
        self.js.evaluate('var transaction={targets:brutallWallpaper("status",{}).targets.map(function(d){return {before:d,after:{plugin:"org.kde.image",image:"new"}};})};')

    def test_apply_and_restore_plugins_without_touching_other_settings(self):
        self.transaction()
        self.value('brutallWallpaper("apply",transaction)')
        self.assertEqual(self.value('ds.map(function(d){return d.image;})'), ["new", "new"])
        self.js.evaluate("ds[0].unrelated=99;")
        self.value('brutallWallpaper("rollback",transaction)')
        self.assertEqual(self.value('ds[0].wallpaperPlugin'), "org.kde.slideshow")
        self.assertEqual(self.value('ds[0].unrelated'), 99)
        self.assertEqual(self.value('ds[1].image'), "old1")

    def test_conflict_on_second_monitor_blocks_every_restore(self):
        self.transaction()
        self.value('brutallWallpaper("apply",transaction)')
        self.js.evaluate('ds[1].image="external";')
        self.assertTrue(self.js.evaluate('brutallWallpaper("rollback",transaction)').isError())
        self.assertEqual(self.value('ds[0].image'), "new")
        self.assertEqual(self.value('ds[1].image'), "external")

    def test_only_selected_monitor_changes_and_topology_change_blocks_apply(self):
        self.transaction()
        self.js.evaluate("transaction.targets=transaction.targets.slice(0,1);")
        self.value('brutallWallpaper("apply",transaction)')
        self.assertEqual(self.value('ds[1].image'), "old1")
        self.transaction()
        self.js.evaluate("ds[0].screen=-1;")
        self.assertTrue(self.js.evaluate('brutallWallpaper("apply",transaction)').isError())
