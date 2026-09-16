"""Estandariza GEIH a un esquema canónico por hogar, para los 12 meses.

Combina el módulo hogar_vivienda (nivel hogar) con las características
del jefe de hogar extraídas de caracteristicas_generales (nivel
persona, filtrado a P6050=="1"), y renombra todo a nombres canónicos
compartidos con el estandarizador de Sisbén (ver
estandarizar_sisben.py), para que el Hot-Deck opere sobre columnas ya
homologadas en vez de tener que mapear nombres cada vez.

⚠️ Verificado con datos reales (2026-09-15), pendiente de confirmar
oficialmente:
  - geo_depto: CONFIRMADO — DPTO (GEIH) y los 2 primeros dígitos de
    cod_mpio (Sisbén) usan el mismo código DIVIPOLA, coincidencia
    exacta de 33 valores.
  - geo_zona: los códigos existen en ambas fuentes (binario 1/2) pero
    NO se confirmó que la dirección sea la misma (¿1=urbano en las
    dos?) — verificar contra el DDI oficial antes de usar esta
    columna como variable de matching fuerte.
  - jefe_sexo / viv_paredes / viv_pisos: mismo caso — código binario o
    categórico presente en ambas fuentes, dirección/categorías no
    verificada oficialmente todavía.

Uso:
    poetry run python -m src.preprocesamiento.estandarizar_geih
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GEIH_DIR = Path("data/1_processed/geih/2024")
OUT_PATH = Path("data/2_models/geih_estandarizado_2024.parquet")

MESES = [f"{m:02d}" for m in range(1, 13)]

# Columnas de hogar_vivienda -> nombre canónico
MAPA_HOGAR_VIVIENDA = {
    "DIRECTORIO": "llave_directorio",
    "SECUENCIA_P": "llave_secuencia_p",
    "HOGAR": "llave_hogar",
    "DPTO": "geo_depto",
    "CLASE": "geo_zona",
    "P4020": "viv_paredes",
    "P4030S1": "viv_pisos",
    "P5010": "viv_cuartos",
    "FEX_C18": "fex",
}

# Columna de caracteristicas_generales (jefe de hogar) -> nombre canónico
MAPA_JEFE = {
    "P3271": "jefe_sexo",
    "P6040": "jefe_edad",
}

FILTRO_JEFE_COL = "P6050"
FILTRO_JEFE_VAL = "1"


def _cargar_mes(mes: str) -> pd.DataFrame | None:
    path_hv = GEIH_DIR / mes / "hogar_vivienda.parquet"
    path_cg = GEIH_DIR / mes / "caracteristicas_generales.parquet"

    if not path_hv.exists():
        logger.warning("GEIH %s: no encontrado (%s) — se omite", mes, path_hv)
        return None

    hv = pd.read_parquet(path_hv).replace("", pd.NA)
    columnas_hv = [c for c in MAPA_HOGAR_VIVIENDA if c in hv.columns]
    hv = hv[["DIRECTORIO", "SECUENCIA_P", "HOGAR", *[c for c in columnas_hv if c not in ("DIRECTORIO", "SECUENCIA_P", "HOGAR")]]]
    hv = hv.rename(columns=MAPA_HOGAR_VIVIENDA)

    if path_cg.exists():
        cg = pd.read_parquet(path_cg).replace("", pd.NA)
        jefes = cg[cg[FILTRO_JEFE_COL] == FILTRO_JEFE_VAL].copy()
        columnas_jefe = [c for c in MAPA_JEFE if c in jefes.columns]
        jefes = jefes[["DIRECTORIO", "SECUENCIA_P", "HOGAR", *columnas_jefe]].rename(columns=MAPA_JEFE)
        hv = hv.merge(
            jefes,
            left_on=["llave_directorio", "llave_secuencia_p", "llave_hogar"],
            right_on=["DIRECTORIO", "SECUENCIA_P", "HOGAR"],
            how="left",
        ).drop(columns=["DIRECTORIO", "SECUENCIA_P", "HOGAR"], errors="ignore")
    else:
        logger.warning("GEIH %s: caracteristicas_generales.parquet no encontrado — sin datos de jefe", mes)

    hv["mes"] = mes
    hv["fuente"] = "geih"
    return hv


def estandarizar_geih() -> pd.DataFrame:
    """Apila los 12 meses de GEIH ya estandarizados. Procesa los meses
    disponibles — no requiere tener los 12 para funcionar."""
    tablas = []
    for mes in MESES:
        df_mes = _cargar_mes(mes)
        if df_mes is not None:
            tablas.append(df_mes)
            logger.info("GEIH %s: %s hogares estandarizados", mes, f"{len(df_mes):,}")

    if not tablas:
        raise RuntimeError("No se encontró ningún mes de GEIH en data/1_processed/geih/2024/")

    resultado = pd.concat(tablas, ignore_index=True)
    return resultado


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = estandarizar_geih()
    df.to_parquet(OUT_PATH, index=False)
    print(f"\n=== GEIH estandarizado ===")
    print(f"Total hogares (todos los meses apilados): {len(df):,}")
    print(df["mes"].value_counts().sort_index())
    print(f"\nGuardado: {OUT_PATH}")


if __name__ == "__main__":
    main()
