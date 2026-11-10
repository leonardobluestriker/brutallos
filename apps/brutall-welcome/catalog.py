"""Stable IDs for onboarding preferences; no shell commands or fake app launchers."""
THEMES = [
    {"id": "bru", "name": "Bru", "variants": [
        {"id": "light", "name": "Claro", "file": "BRULITE.png"},
        {"id": "dark", "name": "Escuro", "file": "BRUDARK.png"},
        {"id": "original", "name": "Original", "file": "BRU1.png"}]},
    {"id": "raio", "name": "Raio", "variants": [
        {"id": "light", "name": "Claro", "file": "RAIOLITE.png"},
        {"id": "dark", "name": "Escuro", "file": "RAIODARK.png"},
        {"id": "original", "name": "Original", "file": "RAIO1.png"}]},
    {"id": "friends", "name": "Strikerzinho & Friends", "variants": [
        {"id": "blue", "name": "Blue Striker", "file": "BLUESTRIKER.png"},
        {"id": "green", "name": "Green Thunder", "file": "GREENTHUNDER.png"},
        {"id": "purple", "name": "Purple Luna", "file": "PURPLELUNA.png"}]},
]
PRESETS = [
    {"id": "creative", "name": "Criativo", "description": "Da primeira ideia ao último frame.",
     "detail": "ArtCraft: Photocraft, Filmcraft, Wordcraft, Gridcraft e Deckcraft."},
    {"id": "developer", "name": "Desenvolvedor", "description": "Um espaço para construir e experimentar.",
     "detail": "Terminal, editor, projetos e monitoramento."},
    {"id": "productivity", "name": "Produtividade", "description": "Menos distração. Mais espaço para organizar.",
     "detail": "ArtCraft: Wordcraft, Gridcraft e Deckcraft; calendário e notas."},
    {"id": "media", "name": "Mídia / Uso caseiro", "description": "Seu intervalo também merece um espaço.",
     "detail": "Navegação, música, vídeos e biblioteca de imagens."},
]
ARTCRAFT = ["Photocraft", "Filmcraft", "Wordcraft", "Gridcraft", "Deckcraft"]


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("As preferências devem ser um objeto JSON.")
    theme = next((t for t in THEMES if t["id"] == data.get("theme")), None)
    if theme is None or data.get("variant") not in {v["id"] for v in theme["variants"]}:
        raise ValueError("Tema ou variante inválida.")
    if data.get("preset") not in {p["id"] for p in PRESETS}:
        raise ValueError("Preset inválido.")
    if data.get("appearance") not in {"system", "light", "dark"}:
        raise ValueError("Aparência inválida.")
    for key in ("highContrast", "reducedMotion", "completed"):
        if type(data.get(key)) is not bool:
            raise ValueError("Preferência inválida: " + key)
    if data.get("schemaVersion") != 1:
        raise ValueError("Versão de preferências não suportada.")
    return data


def defaults():
    return dict(schemaVersion=1, theme="bru", variant="light", preset="creative",
                appearance="system", highContrast=False, reducedMotion=False, completed=False)
