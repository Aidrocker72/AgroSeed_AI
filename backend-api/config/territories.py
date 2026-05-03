import os
import yaml
from typing import List

_YAML_PATH = os.environ.get("TERRITORIES_CONFIG", "/app/territories.yml")

_FALLBACK: List[str] = [
    "Краснодарский край",
    "Ростовская область",
    "Ставропольский край",
    "Воронежская область",
    "Саратовская область",
]


def _load() -> List[str]:
    if not os.path.exists(_YAML_PATH):
        return _FALLBACK
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [t["name"] for t in data.get("territories", [])] or _FALLBACK


TERRITORIES: List[str] = _load()
