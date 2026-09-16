"""Script de limpieza y armonización de fuentes.

Implementado para las 3 tablas de IPM Nacional 2025 disponibles
(Hogares, Personas, Viviendas). Decisiones de limpieza documentadas
según lo encontrado en el diagnóstico de cada tabla en data/0_raw/ipm/:

MODELO DE DATOS (relación entre tablas) — IMPORTANTE, LEER ANTES DE UNIR:
  - Hogares: llave única = DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P
    (79.125 filas, 0 duplicados en esa combinación).
  - Personas: llave única = DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P
    + ORDEN (212.617 filas, 0 duplicados).
  - Viviendas: llave única = DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P
    (78.913 filas, 0 duplicados).
  - ⚠️ PENDIENTE DE VALIDAR: el join Hogares<->Personas usando
    DIRECTORIO+SECUENCIA_ENCUESTA+SECUENCIA_P NO cuadra limpiamente
    (verificado 2026-08-07: usando solo DIRECTORIO+SECUENCIA_ENCUESTA hay
    133.109 combinaciones en Personas sin match en Hogares). Puede deberse
    a que las tres tablas de la descarga "nacional" no son exactamente el
    mismo corte muestral, o a que la semántica de SECUENCIA_P difiere
    entre tablas. NO forzar un join hasta confirmar con la ficha
    metodológica de DANE o con soporte técnico ANDA. Mientras tanto,
    Personas y Viviendas se limpian de forma independiente (no se unen a
    Hogares en este script).

Uso:
    poetry run python src/2_limpieza.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/0_raw/ipm")
OUT_DIR = Path("data/1_processed")
REPORT_DIR = Path("docs/reports")

LLAVE_HOGAR = ["DIRECTORIO", "SECUENCIA_ENCUESTA", "SECUENCIA_P"]
LLAVE_PERSONA = [*LLAVE_HOGAR, "ORDEN"]
LLAVE_VIVIENDA = LLAVE_HOGAR  # misma llave, pero ver nota de validación arriba

# Módulo aplicado solo a una submuestra en HOGARES (~77.79% vacío por
# diseño, no por hogar) — se documentan aparte, no se imputan.
COLUMNAS_SUBMUESTRA_HOGARES = ["PERIODO", "P1075", "P1077S21", "P1077S22", "P1077S23"]

PRIVACIONES = [
    "logro_educativo", "analfabetismo", "inasistencia_escolar", "rezago_escolar",
    "atencion_integral", "trabajo_infantil", "aseguramiento_salud",
    "barreras_acceso_salud", "desempleo_larga_duracion", "empleo_formal",
    "acueducto", "alcantarillado", "pisos", "paredes", "hacinamiento",
]

HOGARES_BINARIAS = [*PRIVACIONES, "POBRE"]
HOGARES_CONTINUAS = ["IPM", "FEX_C", "FEXP", "PERSONAS"]

# Personas y Viviendas: todas las columnas son códigos de pregunta DANE
# (P6020, P4005, etc.) sin re-etiquetar todavía a nombres amigables — ver
# docs/DICCIONARIO_DATOS.md para la traducción código -> etiqueta. Se
# tipan como categóricas (no continuas: son códigos de respuesta, no
# cantidades) salvo ORDEN y FEX_C.
PERSONAS_ID = ["ORDEN"]
PERSONAS_CONTINUAS = ["FEX_C"]

VIVIENDAS_CONTINUAS: list[str] = []  # ninguna en esta tabla (todo categórico)


def _reporte_faltantes(df: pd.DataFrame, columnas_documentadas: dict[str, str]) -> pd.DataFrame:
    """Genera reporte de % faltante por variable, con la acción tomada."""
    faltantes = df.isnull().mean().mul(100).round(2).sort_values(ascending=False)
    reporte = faltantes[faltantes > 0].rename("pct_faltante").reset_index()
    reporte.columns = ["variable", "pct_faltante"]
    reporte["accion"] = reporte["variable"].apply(
        lambda v: columnas_documentadas.get(v, "Revisar manualmente")
    )
    return reporte


def limpiar_hogares(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Limpia y tipa Hogares Nacional. Ver docstring del módulo."""
    df = df.copy().replace("", pd.NA)

    accion_submuestra = (
        "No aplicable a toda la muestra (módulo de submuestra) — "
        "se conserva NaN, no se imputa, se excluye del análisis principal"
    )
    reporte = _reporte_faltantes(
        df, {col: accion_submuestra for col in COLUMNAS_SUBMUESTRA_HOGARES}
    )

    for col in HOGARES_BINARIAS:
        df[col] = df[col].astype("Int8")
    for col in HOGARES_CONTINUAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_dup = df.duplicated(subset=LLAVE_HOGAR).sum()
    if n_dup > 0:
        logger.warning("Hogares: eliminando %s filas duplicadas", n_dup)
        df = df.drop_duplicates(subset=LLAVE_HOGAR, keep="first")

    df["_cleaning_timestamp"] = pd.Timestamp.now().isoformat()
    return df, reporte


def limpiar_personas(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Limpia y tipa Personas Nacional (sin unir a Hogares — ver nota de
    validación de llave en el docstring del módulo)."""
    df = df.copy().replace("", pd.NA)

    reporte = _reporte_faltantes(df, {})  # sin submuestra conocida aquí todavía

    for col in PERSONAS_CONTINUAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # El resto (P6020, P6040, etc.) queda como categórica tipo string —
    # son códigos de respuesta DANE, no cantidades; castear a numérico
    # perdería la semántica categórica.

    n_dup = df.duplicated(subset=LLAVE_PERSONA).sum()
    if n_dup > 0:
        logger.warning("Personas: eliminando %s filas duplicadas", n_dup)
        df = df.drop_duplicates(subset=LLAVE_PERSONA, keep="first")

    df["_cleaning_timestamp"] = pd.Timestamp.now().isoformat()
    return df, reporte


def limpiar_viviendas(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Limpia y tipa Viviendas Nacional (sin unir a Hogares todavía)."""
    df = df.copy().replace("", pd.NA)
    reporte = _reporte_faltantes(df, {})

    n_dup = df.duplicated(subset=LLAVE_VIVIENDA).sum()
    if n_dup > 0:
        logger.warning("Viviendas: eliminando %s filas duplicadas", n_dup)
        df = df.drop_duplicates(subset=LLAVE_VIVIENDA, keep="first")

    df["_cleaning_timestamp"] = pd.Timestamp.now().isoformat()
    return df, reporte


TABLAS = {
    "hogares": (RAW_DIR / "ipm_hogares_nacional.parquet", limpiar_hogares),
    "personas": (RAW_DIR / "ipm_personas_nacional.parquet", limpiar_personas),
    "viviendas": (RAW_DIR / "ipm_viviendas_nacional.parquet", limpiar_viviendas),
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    for nombre, (raw_path, funcion_limpieza) in TABLAS.items():
        if not raw_path.exists():
            logger.error("No se encontró %s — correr primero src/1_integracion.py", raw_path)
            continue

        logger.info("=== %s ===", nombre.upper())
        logger.info("Leyendo %s", raw_path)
        df_raw = pd.read_parquet(raw_path)
        logger.info("Filas crudas: %s", f"{len(df_raw):,}")

        df_limpio, reporte = funcion_limpieza(df_raw)

        out_path = OUT_DIR / f"ipm_{nombre}_nacional_limpio.parquet"
        df_limpio.to_parquet(out_path, index=False)
        logger.info(
            "Guardado: %s (%s filas, %s columnas)",
            out_path, f"{len(df_limpio):,}", df_limpio.shape[1],
        )

        report_path = REPORT_DIR / f"reporte_faltantes_ipm_{nombre}.csv"
        reporte.to_csv(report_path, index=False)
        logger.info("Reporte de faltantes: %s", report_path)

    print("\n=== Resumen de limpieza — IPM Nacional (3 tablas) ===")
    for nombre, (_, _) in TABLAS.items():
        out_path = OUT_DIR / f"ipm_{nombre}_nacional_limpio.parquet"
        if out_path.exists():
            df = pd.read_parquet(out_path)
            print(f"{nombre}: {len(df):,} filas, {df.shape[1]} columnas")
    print(
        "\n⚠️  Personas y Viviendas se limpiaron de forma INDEPENDIENTE, sin "
        "unir a Hogares — la llave de vínculo entre tablas no cuadra "
        "todavía (ver nota en el encabezado de este script). Antes de "
        "usarlas juntas en 3_preprocesamiento.py hay que resolver esto."
    )


if __name__ == "__main__":
    main()

