"""Read-only Linux metrics and freedesktop application discovery."""
import configparser
import locale
import os
from pathlib import Path
import shutil
import time


def applications(roots=None):
    if roots is None:
        roots = [Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")]
        roots += [Path(p) for p in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":") if p.startswith("/")]
    seen, result = set(), []
    language = (locale.getlocale()[0] or "en_US").split(".")[0]
    desktops = set(os.environ.get("XDG_CURRENT_DESKTOP", "KDE").split(":"))
    for root in roots:
        folder = root / "applications"
        for path in sorted(folder.rglob("*.desktop")):
            identifier = str(path.relative_to(folder)).replace("/", "-")
            if identifier in seen:
                continue
            seen.add(identifier)  # Hidden user overrides must mask system entries.
            config = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                config.read_string(path.read_text(encoding="utf-8"))
                item = config["Desktop Entry"]
                if item.get("Type") != "Application" or item.getboolean("Hidden", False) or item.getboolean("NoDisplay", False):
                    continue
                only = set(filter(None, item.get("OnlyShowIn", "").split(";")))
                excluded = set(filter(None, item.get("NotShowIn", "").split(";")))
                if (only and not only.intersection(desktops)) or excluded.intersection(desktops):
                    continue
                if item.get("TryExec") and not shutil.which(item["TryExec"]):
                    continue
                if not item.get("Exec") and not item.getboolean("DBusActivatable", False):
                    continue
                name = item.get("Name[" + language + "]", item.get("Name[" + language.split("_")[0] + "]", item.get("Name", identifier)))
                result.append(dict(id=identifier, name=name, path=str(path.resolve()),
                                   description=item.get("Comment", ""), categories=item.get("Categories", "")))
            except (OSError, UnicodeError, configparser.Error, KeyError, ValueError):
                continue
    return sorted(result, key=lambda entry: entry["name"].casefold())


class Metrics:
    def __init__(self, proc=Path("/proc"), sys=Path("/sys"), disk=Path("/")):
        self.proc, self.sys, self.disk = proc, sys, disk
        self.previous_cpu = None
        self.previous_net = None

    def sample(self):
        result = {"cpu": "Aguardando amostra", "ram": "Indisponível", "disk": "Indisponível",
                  "network": "Indisponível", "gpu": "Indisponível", "temperatures": []}
        try:
            values = [int(v) for v in (self.proc / "stat").read_text().splitlines()[0].split()[1:9]]
            total, idle = sum(values), values[3] + values[4]
            if self.previous_cpu:
                dt, di = total - self.previous_cpu[0], idle - self.previous_cpu[1]
                result["cpu"] = f"{max(0, min(100, 100 * (dt - di) / dt)):.0f}%" if dt > 0 else "Aguardando amostra"
            self.previous_cpu = total, idle
        except (OSError, ValueError, IndexError):
            result["cpu"] = "Indisponível"
        try:
            memory = {line.split(":")[0]: int(line.split()[1]) for line in (self.proc / "meminfo").read_text().splitlines()}
            total, available = memory["MemTotal"], memory["MemAvailable"]
            result["ram"] = f"{(total - available) / 1048576:.1f} / {total / 1048576:.1f} GiB"
        except (OSError, ValueError, KeyError, IndexError):
            pass
        try:
            disk = shutil.disk_usage(self.disk)
            result["disk"] = f"{disk.used / 1073741824:.1f} / {disk.total / 1073741824:.1f} GiB"
        except OSError:
            pass
        try:
            devices = {}
            for line in (self.proc / "net/dev").read_text().splitlines()[2:]:
                name, fields = line.split(":", 1)
                if name.strip() == "lo":
                    continue
                fields = fields.split()
                devices[name.strip()] = int(fields[0]), int(fields[8])
            now = time.monotonic()
            if self.previous_net:
                previous_time, previous = self.previous_net
                elapsed = now - previous_time
                if elapsed > 0:
                    rx = sum(max(0, value[0] - previous[name][0]) for name, value in devices.items() if name in previous)
                    tx = sum(max(0, value[1] - previous[name][1]) for name, value in devices.items() if name in previous)
                    result["network"] = f"↓ {rx / elapsed / 1024:.1f} · ↑ {tx / elapsed / 1024:.1f} KiB/s"
            else:
                result["network"] = "Aguardando amostra"
            self.previous_net = now, devices
        except (OSError, ValueError, IndexError):
            pass
        for hwmon in sorted((self.sys / "class/hwmon").glob("hwmon*")):
            for path in sorted(hwmon.glob("temp*_input")):
                try:
                    name = (hwmon / "name").read_text().strip()
                    label_path = path.with_name(path.name.replace("_input", "_label"))
                    label = label_path.read_text().strip() if label_path.exists() else path.stem
                    temperature = int(path.read_text()) / 1000
                    if -50 <= temperature <= 200:
                        result["temperatures"].append(dict(name=name + " / " + label, value=f"{temperature:.1f} °C"))
                except (OSError, ValueError):
                    continue
        for path in sorted((self.sys / "class/drm").glob("card*/device/gpu_busy_percent")):
            try:
                result["gpu"] = f"{int(path.read_text())}% ({path.parents[1].name})"
                break
            except (OSError, ValueError):
                continue
        return result
