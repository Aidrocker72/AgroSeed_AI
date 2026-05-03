import os
import yaml
from typing import Dict

_YAML_PATH = os.environ.get("TERRITORIES_CONFIG", "/app/territories.yml")

_FALLBACK: Dict[str, float] = {
    "Краснодарский край":  1.05,
    "Ростовская область":  1.00,
    "Ставропольский край": 0.98,
    "Воронежская область": 0.95,
    "Саратовская область": 0.92,
}


def _load() -> Dict[str, float]:
    if not os.path.exists(_YAML_PATH):
        return _FALLBACK
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {t["name"]: t["price_factor"] for t in data.get("territories", [])} or _FALLBACK


TERRITORIES: Dict[str, float] = _load()
