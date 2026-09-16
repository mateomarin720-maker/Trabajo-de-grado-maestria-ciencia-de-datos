"""Loader de GEIH — recorre automáticamente los meses disponibles.

GEIH se descarga de microdatos.dane.gov.co como un ZIP por mes
(Ene_2024.zip ... Dic_2024.zip), cada uno con 8 módulos en CSV/DTA/SAV.
Este loader espera que ya se hayan descomprimido manualmente los ZIP que
se tengan, siguiendo esta estructura uniforme (ver docs/DICCIONARIO_DATOS.md
y data/catalogo.yaml para el detalle):

    data/0_raw/geih/{anio}/{mes_num}/CSV/*.CSV

Donde {mes_num} es "01".."12". Ejemplo, para tener enero 2024 listo:

    1. Descomprimir Ene_2024.zip
    2. Copiar la carpeta CSV/ resultante a data/0_raw/geih/2024/01/CSV/

El loader NO requiere tener los 12 meses — procesa los que encuentre y
avisa cuáles faltan, para que puedan ir corriendo esto progresivamente a
medida que descomprimen cada mes.

Uso:
    poetry run python -m src.ingesta.geih_loader
"""

from __future__ import annotations

import logging
from pathlib import Path

from ingesta.local_csv_parser import parse_csv_a_parquet, parse_stata_a_parquet

logger = logging.getLogger(__name__)

RAW_BASE = Path("data/0_raw/geih")
OUT_BASE = Path("data/1_processed/geih")

MESES = [f"{m:02d}" for m in range(1, 13)]
NOMBRES_MES = {
    "01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr",
    "05": "May", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic",
}


GEIH_ENCODING = "latin1"  # confirmado 2026-08-09: la descarga DANE viene en Latin-1, no UTF-8


# Prefijos ASCII únicos por módulo (más robusto que el nombre completo:
# algunos entornos de descompresión — sobre todo fuera de Windows — dañan
# las tildes de "Características" y "Migración" de forma inconsistente,
# pero el prefijo antes de la primera tilde siempre es ASCII puro y
# suficiente para identificar el archivo sin ambigüedad).
# "No ocupado" (sin "s") porque marzo 2024 trae el archivo en singular
# ("No ocupado.CSV") mientras el resto del año usa plural — el prefijo
# corto matchea ambas variantes.
MODULOS_PREFIJO = {
    "Datos del hogar y la vivienda": "hogar_vivienda",
    "Caracter": "caracteristicas_generales",
    "Fuerza de trabajo": "fuerza_trabajo",
    "No ocupado": "no_ocupados",  # ojo: revisar ANTES que "Ocupados" (substring)
    "Ocupados": "ocupados",
    "Otras formas de trabajo": "otras_formas_trabajo",
    "Otros ingresos e impuestos": "otros_ingresos",
    "Migraci": "migracion",
}


def _buscar_archivo_modulo(carpeta_mes: Path, prefijo: str, extension: str) -> Path | None:
    """Busca el archivo del módulo por prefijo ASCII, en cualquier nivel de
    anidamiento dentro de la carpeta del mes.

    No asume una única carpeta "CSV"/"DTA" candidata: algunos meses (ej.
    marzo y abril 2024) traen varias carpetas con ese nombre por cómo se
    extrajo el ZIP (algunas vacías, "decoy"), así que se busca el archivo
    en toda la carpeta del mes (rglob) en vez de fijarse solo en la
    primera carpeta "CSV" encontrada — evitaba procesar meses donde esa
    primera carpeta resultaba estar vacía.
    """
    candidatos = [f for f in carpeta_mes.rglob(f"*.{extension}") if f.name.startswith(prefijo)]
    if not candidatos:
        return None
    if len(candidatos) > 1:
        logger.warning(
            "  Múltiples archivos '%s*.%s' encontrados para un mismo módulo — "
            "usando el primero: %s",
            prefijo, extension, candidatos[0],
        )
    return candidatos[0]


def ingest_geih(anio: str = "2024") -> dict[str, int]:
    """Procesa todos los meses de GEIH disponibles en data/0_raw/geih/{anio}/.

    Returns:
        Resumen {mes: número de módulos procesados} para los meses que
        sí se encontraron.
    """
    base_anio = RAW_BASE / anio
    if not base_anio.exists():
        logger.warning(
            "No existe %s todavía — crear la carpeta y descomprimir al "
            "menos un mes antes de correr este loader.",
            base_anio,
        )
        return {}

    resumen: dict[str, int] = {}
    meses_faltantes: list[str] = []

    for mes in MESES:
        carpeta_mes = base_anio / mes
        if not carpeta_mes.exists():
            meses_faltantes.append(f"{mes} ({NOMBRES_MES[mes]})")
            continue

        logger.info("=== GEIH %s-%s (%s) ===", anio, mes, NOMBRES_MES[mes])
        procesados = 0
        for prefijo, nombre_salida in MODULOS_PREFIJO.items():
            out_path = OUT_BASE / anio / mes / f"{nombre_salida}.parquet"

            archivo_csv = _buscar_archivo_modulo(carpeta_mes, prefijo, "CSV")
            if archivo_csv is not None:
                resultado = parse_csv_a_parquet(
                    input_path=archivo_csv,
                    output_path=out_path,
                    fuente_id="geih",
                    encoding=GEIH_ENCODING,
                )
                origen = archivo_csv.name
            else:
                # Fallback: el CSV de este módulo no vino o está incompleto
                # en la descarga (caso GEIH agosto 2024, donde solo llegó
                # 1 de 8 CSV pero los 8 .DTA sí estaban completos) — se usa
                # el .DTA equivalente en su lugar.
                archivo_dta = _buscar_archivo_modulo(carpeta_mes, prefijo, "DTA")
                if archivo_dta is None:
                    logger.warning("  Módulo no encontrado (prefijo '%s', ni CSV ni DTA)", prefijo)
                    continue
                logger.warning(
                    "  CSV no encontrado para '%s' — usando .DTA como fallback: %s",
                    prefijo, archivo_dta,
                )
                resultado = parse_stata_a_parquet(
                    input_path=archivo_dta,
                    output_path=out_path,
                    fuente_id="geih",
                )
                origen = archivo_dta.name

            if resultado["status"] == "success":
                procesados += 1
            else:
                logger.error("  Falló %s: %s", origen, resultado.get("error"))

        resumen[mes] = procesados
        logger.info("  %s/%s módulos procesados", procesados, len(MODULOS_PREFIJO))

    if meses_faltantes:
        logger.info(
            "Meses aún no depositados en %s: %s",
            base_anio,
            ", ".join(meses_faltantes),
        )

    return resumen


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    resumen = ingest_geih()
    print("\n=== Resumen GEIH 2024 ===")
    if not resumen:
        print("Ningún mes encontrado en data/0_raw/geih/2024/ todavía.")
    for mes, n in resumen.items():
        print(f"{NOMBRES_MES[mes]} ({mes}): {n}/{len(MODULOS_PREFIJO)} módulos")


if __name__ == "__main__":
    main()
