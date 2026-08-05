"""Configuración centralizada del proyecto.

Carga `data/catalogo.yaml` y las variables de entorno (`.env`) para que
ningún script del pipeline necesite rutas o credenciales hardcodeadas.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
CATALOGO_PATH = ROOT_DIR / "data" / "catalogo.yaml"

load_dotenv(ROOT_DIR / ".env")


def load_catalogo() -> dict[str, Any]:
    """Carga el catálogo de fuentes (`data/catalogo.yaml`)."""
    with open(CATALOGO_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_fuente(fuente_id: str) -> dict[str, Any]:
    """Retorna la entrada del catálogo para una fuente por su `id`.

    Ejemplo: get_fuente("sisben_iv") -> {"nombre": ..., "acceso": ..., ...}
    """
    catalogo = load_catalogo()
    for fuente in catalogo.get("fuentes", []):
        if fuente.get("id") == fuente_id:
            return fuente
    raise KeyError(f"Fuente '{fuente_id}' no encontrada en {CATALOGO_PATH}")


def raw_path(fuente_id: str, *parts: str) -> Path:
    """Construye una ruta dentro de data/0_raw/<fuente_id>/..."""
    return ROOT_DIR / "data" / "0_raw" / fuente_id / Path(*parts)


def processed_path(*parts: str) -> Path:
    """Construye una ruta dentro de data/1_processed/..."""
    return ROOT_DIR / "data" / "1_processed" / Path(*parts)
