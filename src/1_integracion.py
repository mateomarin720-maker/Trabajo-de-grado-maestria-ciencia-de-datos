"""Script de integración de fuentes (ETL) — punto de entrada.

Orquesta la ingesta de todas las fuentes declaradas en
`data/catalogo.yaml`. Para fuentes con `acceso: abierto`, descarga vía
`ingesta.socrata_client`. Para fuentes restringidas, verifica si el
microdato ya fue depositado manualmente en `data/0_raw/<fuente_id>/` y,
si no, deja un log explícito de qué falta gestionar.

Uso:
    poetry run python src/1_integracion.py
"""

from __future__ import annotations

import logging

from ingesta.socrata_client import SocrataClient
from utils.config import load_catalogo, raw_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Dominio Socrata por defecto para fuentes abiertas colombianas.
SOCRATA_DOMAIN = "www.datos.gov.co"


def ingest_abierta(fuente: dict) -> None:
    """Descarga una fuente de acceso abierto vía Socrata."""
    dataset_id = fuente.get("catalogo_ref")
    if not dataset_id:
        logger.warning(
            "Fuente '%s' marcada como abierta pero sin 'catalogo_ref' en "
            "catalogo.yaml — completar el dataset_id de Socrata antes de "
            "ingerir.",
            fuente["id"],
        )
        return

    client = SocrataClient(domain=SOCRATA_DOMAIN)
    df = client.get_dataframe(dataset_id)
    out_path = raw_path(fuente["id"], f"{fuente['id']}.parquet")
    client.save_raw(df, out_path)


def verificar_restringida(fuente: dict) -> None:
    """Verifica si una fuente restringida ya fue depositada manualmente."""
    destino = raw_path(fuente["id"])
    if destino.exists() and any(destino.iterdir()):
        logger.info("Fuente '%s' ya disponible en %s", fuente["id"], destino)
    else:
        logger.warning(
            "Fuente '%s' (%s) pendiente — acceso: %s. Gestionar solicitud "
            "ante %s y depositar el archivo en %s.",
            fuente["id"],
            fuente["nombre"],
            fuente["acceso"],
            fuente["entidad"],
            destino,
        )


def main() -> None:
    catalogo = load_catalogo()
    for fuente in catalogo["fuentes"]:
        logger.info("Procesando fuente: %s (%s)", fuente["id"], fuente["acceso"])
        if fuente["acceso"] == "abierto":
            ingest_abierta(fuente)
        else:
            verificar_restringida(fuente)


if __name__ == "__main__":
    main()
