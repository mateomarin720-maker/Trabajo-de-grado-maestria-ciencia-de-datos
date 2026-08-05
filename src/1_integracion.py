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

from ingesta.local_csv_parser import parse_csv_a_parquet
from ingesta.socrata_client import SocrataClient
from utils.config import load_catalogo, raw_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Dominio Socrata por defecto para fuentes abiertas colombianas.
SOCRATA_DOMAIN = "www.datos.gov.co"

# Archivos CSV locales para fuentes con acceso=registro que ya tenemos
# depositados manualmente (ver data/catalogo.yaml). Ruta relativa a
# data/0_raw/<fuente_id>/. Ajustar aquí si cambia la estructura de
# carpetas al descomprimir la descarga de microdatos.dane.gov.co.
ARCHIVOS_LOCALES = {
    "ipm": [
        ("nacional/hogares.csv", "ipm_hogares_nacional.parquet"),
        ("nacional/personas.csv", "ipm_personas_nacional.parquet"),
        ("nacional/viviendas.csv", "ipm_viviendas_nacional.parquet"),
        ("departamental/hogares.csv", "ipm_hogares_departamental.parquet"),
        ("departamental/personas.csv", "ipm_personas_departamental.parquet"),
        ("departamental/viviendas.csv", "ipm_viviendas_departamental.parquet"),
    ],
}


def ingest_local_csv(fuente: dict) -> None:
    """Procesa los CSV locales ya depositados para una fuente (p. ej. IPM)."""
    fuente_id = fuente["id"]
    archivos = ARCHIVOS_LOCALES.get(fuente_id)
    if not archivos:
        logger.info(
            "Fuente '%s' sin CSV locales configurados en ARCHIVOS_LOCALES "
            "todavía — nada que hacer.",
            fuente_id,
        )
        return

    base = raw_path(fuente_id)
    procesados = 0
    for rel_input, out_name in archivos:
        input_path = base / rel_input
        if not input_path.exists():
            logger.warning("No encontrado (se omite): %s", input_path)
            continue
        resultado = parse_csv_a_parquet(
            input_path=input_path,
            output_path=base / out_name,
            fuente_id=fuente_id,
        )
        if resultado["status"] == "success":
            procesados += 1
    logger.info("Fuente '%s': %s/%s archivos procesados", fuente_id, procesados, len(archivos))


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
    """Verifica si una fuente restringida ya fue depositada manualmente.

    Si además hay un procesador local configurado en ARCHIVOS_LOCALES
    (p. ej. IPM), lo corre; si no, solo avisa qué falta gestionar.
    """
    destino = raw_path(fuente["id"])
    if destino.exists() and any(destino.iterdir()):
        logger.info("Fuente '%s' ya disponible en %s", fuente["id"], destino)
        if fuente["id"] in ARCHIVOS_LOCALES:
            ingest_local_csv(fuente)
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
