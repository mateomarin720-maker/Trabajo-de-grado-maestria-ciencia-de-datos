"""Estandariza Sisbén IV 2024 a un esquema canónico por hogar.

Combina Hogares + Viviendas + características del jefe de hogar y
tratamiento (Grupo/Nivel/Clasificacion) desde Personas (filtrado a
PER003=="1"), renombrado a los MISMOS nombres canónicos que usa
estandarizar_geih.py, para que el Hot-Deck compare columnas ya
homologadas.

Ver advertencias de codificación pendientes de verificar oficialmente
en el docstring de estandarizar_geih.py — aplican igual aquí.

Uso:
    poetry run python -m src.preprocesamiento.estandarizar_sisben
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SISBEN_DIR = Path("data/1_processed/sisben_iv/2024")
OUT_PATH = Path("data/2_models/sisben_estandarizado_2024.parquet")

MAPA_HOGAR = {
    "cod_mpio": "_cod_mpio",  # se deriva geo_depto de aquí, no se usa directo
    "ZONA": "geo_zona",
    "HOG027": "hog_num_personas",
    "FEX": "fex",
}
MAPA_VIVIENDA = {
    "VIV002": "viv_paredes",
    "VIV003": "viv_pisos",
    "VIV005": "viv_alcantarillado",
    "VIV008": "viv_acueducto",
    "VIV009": "viv_cuartos",
}
MAPA_JEFE = {
    "PER001": "jefe_sexo",
    "PER002": "jefe_edad",
}

FILTRO_JEFE_COL = "PER003"
FILTRO_JEFE_VAL = "1"

LLAVE = ["cod_mpio", "ZONA", "llave", "CORTE"]


def estandarizar_sisben() -> pd.DataFrame:
    cols_hog = [*LLAVE, "HOGAR", *MAPA_HOGAR.keys()]
    cols_hog = list(dict.fromkeys(cols_hog))  # sin duplicados, conserva orden
    hog = pd.read_parquet(SISBEN_DIR / "hogares.parquet", columns=cols_hog).replace("", pd.NA)

    cols_viv = [*LLAVE, *MAPA_VIVIENDA.keys()]
    cols_viv = list(dict.fromkeys(cols_viv))
    viv = pd.read_parquet(SISBEN_DIR / "viviendas.parquet", columns=cols_viv).replace("", pd.NA)

    cols_pers = [*LLAVE, "HOGAR", FILTRO_JEFE_COL, *MAPA_JEFE.keys(), "Grupo", "Nivel", "Clasificacion"]
    cols_pers = list(dict.fromkeys(cols_pers))
    pers = pd.read_parquet(SISBEN_DIR / "personas.parquet", columns=cols_pers).replace("", pd.NA)

    jefes = pers[pers[FILTRO_JEFE_COL] == FILTRO_JEFE_VAL].copy()
    n_dup_jefe = jefes.duplicated(subset=[*LLAVE, "HOGAR"]).sum()
    if n_dup_jefe > 0:
        logger.warning(
            "Sisbén: %s hogares con más de un 'jefe' marcado (PER003==1, "
            "posible error de captura) — se conserva solo el primero por hogar",
            n_dup_jefe,
        )
        jefes = jefes.drop_duplicates(subset=[*LLAVE, "HOGAR"], keep="first")

    n_hogares = hog[["cod_mpio", "ZONA", "llave", "CORTE", "HOGAR"]].drop_duplicates().shape[0]
    logger.info(
        "Sisbén: %s hogares totales, %s con jefe identificado (%.1f%%)",
        f"{n_hogares:,}", f"{len(jefes):,}", 100 * len(jefes) / n_hogares,
    )
    del pers

    df = hog.merge(viv, on=LLAVE, how="left")
    df = df.merge(jefes, on=[*LLAVE, "HOGAR"], how="left")

    df = df.rename(columns={**MAPA_HOGAR, **MAPA_VIVIENDA, **MAPA_JEFE})
    df["geo_depto"] = df["_cod_mpio"].astype(str).str[:2]
    df = df.drop(columns=["_cod_mpio"], errors="ignore")
    df["fuente"] = "sisben_iv"

    return df


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = estandarizar_sisben()
    df.to_parquet(OUT_PATH, index=False)
    print("\n=== Sisbén estandarizado ===")
    print(f"Total hogares: {len(df):,}")
    print(f"Con tratamiento (Clasificacion) asignado: {df['Clasificacion'].notna().sum():,}")
    print(f"\nGuardado: {OUT_PATH}")


if __name__ == "__main__":
    main()
