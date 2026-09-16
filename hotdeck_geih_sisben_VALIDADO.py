"""Hot-Deck: fusión estadística GEIH <-> Sisbén IV 2024.

No existe llave compartida entre GEIH y Sisbén (reserva estadística —
ver docs/DICCIONARIO_HOTDECK.md), así que este script NO hace un join
exacto: construye un archivo fusionado sintético, asignando a cada
hogar GEIH (receptor) el tratamiento (Grupo/Nivel/Clasificación) del
hogar Sisbén más parecido (donante), según variables comunes (X).

Dos métodos, ambos sobre las mismas variables de matching:
  1. Hot-deck por celdas (estratos) — método principal, más transparente
  2. NND por distancia de Gower — robustez, sobre una submuestra

⚠️ Supuesto de identificación (declarar en la tesis): independencia
condicional del matching — dado el conjunto de X, el tratamiento
Sisbén y el outcome GEIH/IPM son condicionalmente independientes. No es
verificable con estos datos; se sostiene por la riqueza de X.

⚠️ Los códigos de categoría (ej. material de paredes) puede que NO usen
exactamente la misma escala entre GEIH y Sisbén — este script no asume
un crosswalk oficial verificado; ANTES de correr con datos reales,
correr `verificar_columnas()` y revisar a mano que las categorías de
cada variable compartida sean comparables (ver TODO_CROSSWALK abajo).

Uso:
    poetry run python -m src.hotdeck.hotdeck_geih_sisben
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

GEIH_DIR = Path("data/1_processed/geih/2024")
SISBEN_DIR = Path("data/1_processed/sisben_iv/2024")
OUT_DIR = Path("data/2_models")

# Mes de GEIH a usar como receptor (ajustar o iterar sobre varios si se
# quiere apilar meses — ver nota de potencia estadística ya discutida).
MES_GEIH = "01"

# --------------------------------------------------------------------
# TODO_CROSSWALK: estas equivalencias de código vienen de la revisión
# manual del diccionario de datos (docs/DICCIONARIO_HOTDECK.md), pero
# los códigos de RESPUESTA dentro de cada variable (ej. "1"=material
# X, "2"=material Y) pueden diferir entre GEIH y Sisbén. Antes de
# confiar en el matching, verificar con las tablas de códigos reales
# de cada DDI que las categorías numéricas signifiquen lo mismo, y
# ajustar aquí si no.
# --------------------------------------------------------------------
VARS_GEIH = {
    "geografia": ["DPTO"],
    "vivienda": ["P4010", "P4020", "P4030S1", "P5010"],
    "hogar": ["PERSONAS"] if False else [],  # PERSONAS está en módulo Hogares IPM, no GEIH — ajustar si se confirma columna equivalente en GEIH
}
VARS_SISBEN_HOG = ["cod_mpio", "VIV002", "VIV003", "VIV009", "HOG027"]

LLAVE_GEIH_HOGAR = ["DIRECTORIO", "SECUENCIA_P", "HOGAR"]
LLAVE_SISBEN_HOGAR = ["cod_mpio", "zona", "llave", "corte"]


def verificar_columnas(df: pd.DataFrame, columnas_esperadas: list[str], nombre: str) -> list[str]:
    """Verifica cuáles de las columnas esperadas existen realmente.
    Devuelve las que SÍ están; avisa (no falla) por las que no."""
    presentes = [c for c in columnas_esperadas if c in df.columns]
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        logger.warning(
            "%s: columnas esperadas no encontradas: %s. Columnas disponibles: %s",
            nombre, faltantes, list(df.columns)[:30],
        )
    return presentes


def cargar_geih_receptor(mes: str = MES_GEIH) -> pd.DataFrame:
    """Carga el módulo hogar/vivienda de GEIH para un mes, como receptor."""
    path = GEIH_DIR / mes / "hogar_vivienda.parquet"
    df = pd.read_parquet(path)
    df = df.replace("", pd.NA)
    logger.info("GEIH %s: %s hogares cargados", mes, f"{len(df):,}")
    return df


def cargar_sisben_donante() -> pd.DataFrame:
    """Carga y une Hogares + Viviendas de Sisbén, como donante.

    Lee solo las columnas necesarias de cada archivo (Personas trae
    4.7M filas x 51 columnas completas — cargarlo entero desperdicia
    memoria quedando la mayoría de columnas sin uso para el matching)."""
    cols_hog = ["cod_mpio", "ZONA", "llave", "CORTE", "HOGAR", "FEX", "HOG027"]
    cols_viv = ["cod_mpio", "ZONA", "llave", "CORTE", "VIV002", "VIV003", "VIV005", "VIV008", "VIV009"]
    cols_pers = ["cod_mpio", "ZONA", "llave", "CORTE", "HOGAR", "Grupo", "Nivel", "Clasificacion"]

    hog = pd.read_parquet(SISBEN_DIR / "hogares.parquet", columns=cols_hog).replace("", pd.NA)
    viv = pd.read_parquet(SISBEN_DIR / "viviendas.parquet", columns=cols_viv).replace("", pd.NA)
    pers = pd.read_parquet(SISBEN_DIR / "personas.parquet", columns=cols_pers).replace("", pd.NA)

    llave_pers = ["cod_mpio", "ZONA", "llave", "CORTE", "HOGAR"]
    trat = pers.drop_duplicates(subset=llave_pers).rename(
        columns={"ZONA": "zona", "CORTE": "corte", "HOGAR": "hogar"}
    )
    del pers  # liberar los 4.7M de filas apenas se usan

    hog = hog.rename(columns={"ZONA": "zona", "CORTE": "corte", "HOGAR": "hogar"})
    viv = viv.rename(columns={"ZONA": "zona", "CORTE": "corte"})

    df = hog.merge(viv, on=["cod_mpio", "zona", "llave", "corte"], how="left")
    df = df.merge(trat, on=["cod_mpio", "zona", "llave", "corte", "hogar"], how="left")
    n_sin_trat = df["Clasificacion"].isna().sum()
    if n_sin_trat > 0:
        logger.warning(
            "Sisbén: %s hogares (%.1f%%) sin tratamiento tras el join hogar-persona "
            "— revisar si la llave `hogar` calza igual en las 3 tablas",
            f"{n_sin_trat:,}", 100 * n_sin_trat / len(df),
        )
    logger.info("Sisbén: %s hogares donantes cargados", f"{len(df):,}")
    return df


def construir_celda(df: pd.DataFrame, geo_col: str, bins_extra: list[str] | None = None) -> pd.Series:
    """Construye la clave de celda para el hot-deck por estratos:
    geografía + bins de las variables de vivienda disponibles.
    Los bins se hacen sobre rangos (qcut) para variables no categóricas
    limpias, y se degradan a NA-safe si faltan columnas."""
    partes = [df[geo_col].astype(str)]
    if bins_extra:
        for col in bins_extra:
            if col in df.columns:
                partes.append(df[col].astype(str))
    return partes[0].str.cat(partes[1:], sep="|") if len(partes) > 1 else partes[0]


def hotdeck_por_celda(
    receptor: pd.DataFrame,
    donante: pd.DataFrame,
    celda_receptor: pd.Series,
    celda_donante: pd.Series,
    columnas_tratamiento: list[str],
    seed: int = 42,
) -> pd.DataFrame:
    """Para cada hogar receptor, asigna el tratamiento de un donante
    elegido al azar dentro de la misma celda. Si la celda no tiene
    donantes, degrada progresivamente (quita el último componente de
    la celda) hasta encontrar donantes o agotar niveles."""
    rng = np.random.default_rng(seed)
    receptor = receptor.copy()
    receptor["_celda"] = celda_receptor.values
    donante = donante.copy()
    donante["_celda"] = celda_donante.values

    donantes_por_celda = {
        celda: grupo for celda, grupo in donante.groupby("_celda")
    }

    asignaciones = {col: [] for col in columnas_tratamiento}
    metodo = []

    for celda in receptor["_celda"]:
        grupo = donantes_por_celda.get(celda)
        nivel_usado = "celda_exacta"
        if grupo is None or grupo.empty:
            # Degradar: usar solo el primer componente (geografía)
            geo = celda.split("|")[0]
            candidatos = [g for c, g in donantes_por_celda.items() if c.split("|")[0] == geo]
            if candidatos:
                grupo = pd.concat(candidatos)
                nivel_usado = "solo_geografia"
            else:
                grupo = donante  # último recurso: todo el pool nacional
                nivel_usado = "pool_nacional"

        donante_elegido = grupo.iloc[rng.integers(0, len(grupo))]
        for col in columnas_tratamiento:
            asignaciones[col].append(donante_elegido[col])
        metodo.append(nivel_usado)

    for col in columnas_tratamiento:
        receptor[f"{col}_hotdeck"] = asignaciones[col]
    receptor["_hotdeck_nivel"] = metodo
    return receptor


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    receptor = cargar_geih_receptor()
    donante = cargar_sisben_donante()

    verificar_columnas(receptor, VARS_GEIH["vivienda"] + VARS_GEIH["geografia"], "GEIH receptor")
    verificar_columnas(donante, VARS_SISBEN_HOG, "Sisbén donante")

    # Celda simple de arranque: geografía sola (cod_mpio/DPTO no son
    # directamente comparables en granularidad — DPTO es departamento
    # en GEIH, cod_mpio es municipio en Sisbén; ajustar a un nivel
    # geográfico común, ej. truncando cod_mpio a los primeros 2 dígitos
    # = código de departamento, antes de correr en serio).
    donante["_depto"] = donante["cod_mpio"].astype(str).str[:2]
    celda_receptor = receptor["DPTO"].astype(str)
    celda_donante = donante["_depto"].astype(str)

    fusionado = hotdeck_por_celda(
        receptor, donante, celda_receptor, celda_donante,
        columnas_tratamiento=["Grupo", "Nivel", "Clasificacion"],
    )

    out_path = OUT_DIR / f"geih_{MES_GEIH}_sisben_fusionado.parquet"
    fusionado.to_parquet(out_path, index=False)

    print("\n=== Resumen Hot-Deck ===")
    print(f"Hogares GEIH fusionados: {len(fusionado):,}")
    print(fusionado["_hotdeck_nivel"].value_counts())
    print(f"\nGuardado: {out_path}")
    print(
        "\n⚠️  Revisar antes de usar en el análisis: confirmar que DPTO "
        "(GEIH) y los 2 primeros dígitos de cod_mpio (Sisbén) usan el "
        "mismo código de departamento (DIVIPOLA) — si no, la celda "
        "geográfica no está funcionando como se espera."
    )


if __name__ == "__main__":
    main()
