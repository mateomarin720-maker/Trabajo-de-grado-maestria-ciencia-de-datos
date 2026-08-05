"""Script de limpieza y armonización de fuentes.

Implementado primero para IPM Hogares Nacional 2025 (la primera fuente
real disponible del proyecto). Decisiones de limpieza documentadas según
lo encontrado en el diagnóstico de data/0_raw/ipm/ipm_hogares_nacional.parquet:

1. Llave única de hogar: DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P
   (DIRECTORIO solo NO es único — es el segmento muestral, no el hogar;
   tiene 212 duplicados en la base nacional).
2. Columnas P1075, P1077S21, P1077S22, P1077S23, PERIODO tienen ~77.79%
   de vacíos EN LAS CINCO por igual — es un módulo aplicado solo a una
   submuestra (missing por diseño, no por hogar). NO se imputan; se
   documentan como "no aplicable a toda la muestra" y se excluyen del
   análisis principal salvo que se necesiten puntualmente.
3. Los vacíos llegan de 0_raw como string vacío "" (el ingestor usa
   keep_default_na=False para no perder ceros reales como texto) — se
   convierten explícitamente a NaN aquí.
4. Las 15 privaciones + POBRE son binarias (0/1) -> Int8 con soporte NA.
   IPM es continuo [0,1] -> float64. FEX_C/FEXP son factores de
   expansión -> float64. Identificadores quedan como string (no se
   castean a numérico: son códigos, no cantidades).

Uso:
    poetry run python src/2_limpieza.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_PATH = Path("data/0_raw/ipm/ipm_hogares_nacional.parquet")
OUT_PATH = Path("data/1_processed/ipm_hogares_nacional_limpio.parquet")
REPORT_PATH = Path("docs/reports/reporte_faltantes_ipm_hogares.csv")

LLAVE_HOGAR = ["DIRECTORIO", "SECUENCIA_ENCUESTA", "SECUENCIA_P"]

# Módulo aplicado solo a una submuestra (~77.79% vacío por diseño, no por
# hogar) — se documentan aparte, no se imputan ni se usan en el análisis
# principal de privaciones/IPM.
COLUMNAS_SUBMUESTRA = ["PERIODO", "P1075", "P1077S21", "P1077S22", "P1077S23"]

PRIVACIONES = [
    "logro_educativo", "analfabetismo", "inasistencia_escolar", "rezago_escolar",
    "atencion_integral", "trabajo_infantil", "aseguramiento_salud",
    "barreras_acceso_salud", "desempleo_larga_duracion", "empleo_formal",
    "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento",
]

COLUMNAS_BINARIAS = [*PRIVACIONES, "POBRE"]
COLUMNAS_CONTINUAS = ["IPM", "FEX_C", "FEXP", "PERSONAS"]


def limpiar_ipm_hogares(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Limpia y tipa el DataFrame crudo de IPM Hogares Nacional.

    Returns:
        (df_limpio, reporte_faltantes)
    """
    df = df.copy()

    # 1. Vacíos reales: "" -> NaN (solo aplica a las columnas de submuestra
    #    en este dataset; el resto no tiene vacíos).
    df = df.replace("", pd.NA)

    # 2. Reporte de faltantes ANTES de cualquier decisión de imputación
    #    (checklist pide esto explícito por variable, no una regla ciega).
    faltantes = df.isnull().mean().mul(100).round(2).sort_values(ascending=False)
    reporte = faltantes[faltantes > 0].rename("pct_faltante").reset_index()
    reporte.columns = ["variable", "pct_faltante"]
    reporte["accion"] = reporte["variable"].apply(
        lambda v: (
            "No aplicable a toda la muestra (módulo de submuestra) — "
            "se conserva NaN, no se imputa, se excluye del análisis principal"
        )
        if v in COLUMNAS_SUBMUESTRA
        else "Revisar manualmente"
    )

    # 3. Tipado explícito
    for col in COLUMNAS_BINARIAS:
        df[col] = df[col].astype("Int8")  # soporta NA, a diferencia de int8 nativo
    for col in COLUMNAS_CONTINUAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Duplicados a nivel de la llave real de hogar (no DIRECTORIO solo)
    n_dup = df.duplicated(subset=LLAVE_HOGAR).sum()
    if n_dup > 0:
        logger.warning("Eliminando %s filas duplicadas por llave de hogar", n_dup)
        df = df.drop_duplicates(subset=LLAVE_HOGAR, keep="first")

    # 5. Trazabilidad de la limpieza
    df["_cleaning_timestamp"] = pd.Timestamp.now().isoformat()

    return df, reporte


def main() -> None:
    if not RAW_PATH.exists():
        logger.error(
            "No se encontró %s — correr primero src/1_integracion.py", RAW_PATH
        )
        return

    logger.info("Leyendo %s", RAW_PATH)
    df_raw = pd.read_parquet(RAW_PATH)
    logger.info("Filas crudas: %s", f"{len(df_raw):,}")

    df_limpio, reporte = limpiar_ipm_hogares(df_raw)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_limpio.to_parquet(OUT_PATH, index=False)
    logger.info("Guardado: %s (%s filas, %s columnas)", OUT_PATH, f"{len(df_limpio):,}", df_limpio.shape[1])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    reporte.to_csv(REPORT_PATH, index=False)
    logger.info("Reporte de faltantes: %s", REPORT_PATH)

    print("\n=== Resumen de limpieza — IPM Hogares Nacional ===")
    print(f"Filas: {len(df_raw):,} -> {len(df_limpio):,}")
    print(f"Tasa de pobreza (POBRE=1): {df_limpio['POBRE'].mean() * 100:.1f}%")
    print(f"IPM promedio: {df_limpio['IPM'].mean():.3f}")
    print("\nFaltantes por variable:")
    print(reporte.to_string(index=False))


if __name__ == "__main__":
    main()
