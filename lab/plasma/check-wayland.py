"""Real Wayland outputs and per-output panel isolation in the disposable lab."""
import json
import subprocess
import time
from pathlib import Path

QDBUS = "/usr/lib/qt6/bin/qdbus"


def evaluate(code):
    return subprocess.check_output([QDBUS, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", code], text=True).strip()


def command(script, action, screen, *extra):
    return json.loads(subprocess.check_output(["/project/scripts/" + script, action, "--screen", str(screen), *extra], text=True))


count = int(evaluate("print(screenCount)"))
assert count >= 1
Path("/results/wayland-initial-layout.js").write_text(subprocess.check_output([
    QDBUS, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.dumpCurrentLayoutJS"], text=True))
# Disposable laboratory fixture; never performed by the product's installer.
evaluate("var p=panels(); for(var i=0;i<p.length;i++) p[i].remove(); print('cleared');")
time.sleep(2)
created = []
for screen in range(count):
    created.append({"top": command("brutall-top-panel", "apply", screen), "dock": command("brutall-dock", "apply", screen)})
    assert created[-1]["top"]["state"] == created[-1]["dock"]["state"] == "created"
    assert command("brutall-dock", "apply", screen)["state"] == "unchanged"
if count > 1:
    assert command("brutall-dock", "rollback", 1, "--backup", created[1]["dock"]["backup"])["state"] == "removed"
    assert len(command("brutall-dock", "status", 0)["existing"]) == 1
    created[1]["dock"] = command("brutall-dock", "apply", 1)
evaluate("var ds=desktops(); for(var i=0;i<ds.length;i++){ds[i].wallpaperPlugin='org.kde.image';ds[i].currentConfigGroup=['Wallpaper','org.kde.image','General'];ds[i].writeConfig('Image', i===0?'file:///project/assets/wallpapers/BRU1.png':'file:///project/assets/wallpapers/RAIO1.png');} print('set');")
subprocess.run(["plasma-apply-colorscheme", "BreezeDark"], check=True)
subprocess.run(["plasma-apply-desktoptheme", "breeze-dark"], check=True)
report = {"session": "Wayland nested on Xvfb", "screens": count, "created": created,
          "crossScreenRollback": count > 1, "screenGeometry": evaluate("var g=[]; for(var i=0;i<screenCount;i++) {var r=screenGeometry(i);g.push({x:r.x,y:r.y,width:r.width,height:r.height});} print(JSON.stringify(g));")}
Path("/results/wayland-integration.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
