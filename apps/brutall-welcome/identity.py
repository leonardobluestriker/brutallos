"""Shared theme colors, contrast and persisted interface settings (no Qt dependency)."""
import json
import re
import configparser
import io
from pathlib import Path
from catalog import THEMES


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", value):
        raise ValueError("Use uma cor hexadecimal: #RGB ou #RRGGBB.")
    value = value[1:].lower()
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return "#" + value


def rgb(value):
    value = color(value)
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def mix(base, tone, amount):
    return "#" + "".join(f"{round(a * (1 - amount) + b * amount):02x}" for a, b in zip(rgb(base), rgb(tone)))


def luminance(value):
    channels = [c / 255 for c in rgb(value)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    a, b = sorted((luminance(a), luminance(b)))
    return (b + 0.05) / (a + 0.05)


def readable(tone, backgrounds, minimum):
    target = "#ffffff" if luminance(backgrounds[0]) < 0.3 else "#000000"
    for step in range(101):
        candidate = mix(tone, target, step / 100)
        if all(contrast(candidate, background) >= minimum for background in backgrounds):
            return candidate
    return target


def palette(accent, dark, tinted=True):
    accent = color(accent)
    paper = "#151827" if dark else "#f6f7fc"
    surface = "#202538" if dark else "#edf0f8"
    if tinted:
        paper = mix(paper, accent, 0.10 if dark else 0.06)
        surface = mix(surface, accent, 0.15 if dark else 0.10)
    foreground = max(("#000000", "#ffffff"), key=lambda candidate: contrast(candidate, accent))
    return dict(accent=accent, accentText=foreground, paper=paper, surface=surface,
                ink="#f8f9ff" if dark else "#101322", muted="#bac2d9" if dark else "#50576b",
                border="#69728d" if dark else "#9199ae",
                hover=mix(surface, accent, 0.13),
                focus=readable(accent, [paper, surface], 3),
                link=readable(accent, [paper, surface], 4.5))


def variant(theme_id, variant_id):
    theme = next((t for t in THEMES if t["id"] == theme_id), None)
    chosen = next((v for v in theme["variants"] if v["id"] == variant_id), None) if theme else None
    if chosen is None:
        raise ValueError("Tema ou variante inválida.")
    return chosen


def settings(theme="bru", selected="original", accent=None, tinted=True, mode="light"):
    variant(theme, selected)
    if type(tinted) is not bool or mode not in {"light", "dark"}:
        raise ValueError("Aparência inválida.")
    return dict(schemaVersion=1, theme=theme, variant=selected,
                accent=color(accent) if accent is not None else None, tinted=tinted, mode=mode)


def read_settings(path, dark=False):
    path = Path(path)
    if path.exists():
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or data.get("schemaVersion") != 1:
            raise ValueError("Preferência de interface inválida.")
        return settings(data["theme"], data["variant"], data["accent"], data["tinted"], data["mode"])
    # Onboarding preferences supply the initial identity without modifying them.
    welcome = path.with_name("welcome.json")
    if welcome.exists():
        try:
            data = json.loads(welcome.read_text())
            return settings(data["theme"], data["variant"], mode="dark" if dark else "light")
        except (ValueError, KeyError, TypeError):
            pass
    return settings(mode="dark" if dark else "light")


def color_scheme(template, identity):
    """Keep semantic colors, replacing identity colors and neutral surfaces."""
    p = palette(identity["accent"] or variant(identity["theme"], identity["variant"])["accent"],
                identity["mode"] == "dark", identity["tinted"])
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_string(template)
    config["General"].update(Name="BrutallIdentity", ColorScheme="BrutallIdentity", TintFactor="0")
    def native(value): return ",".join(map(str, rgb(value)))
    for section in config.sections():
        if not section.startswith("Colors:"):
            continue
        tones = p
        if section in {"Colors:Tooltip", "Colors:Complementary"}:
            tones = palette(p["accent"], True, identity["tinted"])
        background = tones["surface"] if section == "Colors:Button" else tones["paper"]
        config[section].update({key: native(value) for key, value in {
            "BackgroundNormal": background, "BackgroundAlternate": tones["surface"],
            "ForegroundNormal": tones["ink"], "ForegroundInactive": tones["muted"],
            "ForegroundActive": tones["link"], "ForegroundLink": tones["link"],
            "DecorationFocus": tones["focus"], "DecorationHover": tones["focus"],
        }.items()})
    config["Colors:Selection"].update(BackgroundNormal=native(p["accent"]),
                                       BackgroundAlternate=native(p["accent"]),
                                       ForegroundNormal=native(p["accentText"]),
                                       ForegroundInactive=native(p["accentText"]))
    config["WM"].update({key: native(p[value]) for key, value in {
        "activeBackground": "paper", "inactiveBackground": "paper",
        "activeBlend": "paper", "inactiveBlend": "paper",
        "activeForeground": "ink", "inactiveForeground": "muted",
    }.items()})
    output = io.StringIO()
    config.write(output, space_around_delimiters=False)
    return output.getvalue().encode()
