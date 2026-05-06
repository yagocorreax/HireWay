import json
from pathlib import Path


MATERIALS_PATH = Path("data/knowledge_base/Material.json")


def load_materials() -> list[dict]:
    if not MATERIALS_PATH.exists():
        raise FileNotFoundError(f"Materials file not found: {MATERIALS_PATH}")

    with open(MATERIALS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)