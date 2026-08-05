"""
Validador de deduplicación entre fuentes vinculadas (OE4).

Adaptado de `scripts/validar_proveedores.py` del repo de referencia
`desarrollo_social_y_economico` (rama `develop`), que detecta doble conteo
al combinar SECOP I y SECOP II por NIT de proveedor. Aquí el mismo
principio aplica a hogares: tras el statistical matching entre GEIH y
Sisbén IV (ver docs/Anteproyecto_Sisben_IV.docx, sección 4.3), un mismo
hogar puede quedar representado más de una vez si el linkage no es
estrictamente 1:1 a nivel de `hogar_id` (o del identificador puente que
se use del Registro Social de Hogares).

Calcula, por unidad territorial (departamento/municipio) y fuente:
- "suma naíve": conteo de hogares en cada fuente, sumados sin deduplicar.
- "unión verdadera": COUNT(DISTINCT hogar_id) sobre el combinado.
- diferencia = doble conteo evitado, y su % sobre el total.

Uso (una vez existan los Parquet limpios en data/1_processed/):

    poetry run python src/utils/validar_linkage.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Columnas esperadas tras 2_limpieza.py / 3_preprocesamiento.py.
# Ajustar cuando se conozca el esquema real de GEIH y Sisbén IV procesados.
COL_ID_HOGAR = "hogar_id"
COL_TERRITORIO = "divipola_municipio"


def validar_doble_conteo(
    df_geih: pd.DataFrame,
    df_sisben: pd.DataFrame,
    id_col: str = COL_ID_HOGAR,
    territorio_col: str = COL_TERRITORIO,
) -> pd.DataFrame:
    """Compara conteo naíve vs. unión verdadera de hogares entre dos fuentes.

    Args:
        df_geih: DataFrame de GEIH procesado, con columnas [id_col, territorio_col].
        df_sisben: DataFrame de Sisbén IV procesado, mismas columnas.
        id_col: columna identificadora única de hogar tras el linkage.
        territorio_col: columna de agregación territorial (p. ej. municipio).

    Returns:
        DataFrame con conteo naíve, unión verdadera y % de doble conteo,
        por unidad territorial.
    """
    for nombre, df in [("GEIH", df_geih), ("Sisbén IV", df_sisben)]:
        faltantes = {id_col, territorio_col} - set(df.columns)
        if faltantes:
            raise ValueError(f"Faltan columnas {faltantes} en el DataFrame de {nombre}")

    a = df_geih[[territorio_col, id_col]].dropna().copy()
    a["fuente"] = "GEIH"
    b = df_sisben[[territorio_col, id_col]].dropna().copy()
    b["fuente"] = "SISBEN_IV"

    combinado = pd.concat([a, b], ignore_index=True)

    solo_a = a.groupby(territorio_col)[id_col].nunique().rename("hogares_geih")
    solo_b = b.groupby(territorio_col)[id_col].nunique().rename("hogares_sisben")
    union = combinado.groupby(territorio_col)[id_col].nunique().rename("union_verdadera")

    resultado = pd.concat([solo_a, solo_b, union], axis=1).fillna(0).reset_index()
    resultado["suma_naiva"] = resultado["hogares_geih"] + resultado["hogares_sisben"]
    resultado["doble_conteo"] = resultado["suma_naiva"] - resultado["union_verdadera"]
    resultado["pct_doble_conteo"] = (
        resultado["doble_conteo"] / resultado["suma_naiva"].replace(0, pd.NA) * 100
    )

    return resultado.sort_values(territorio_col)


def main() -> None:
    processed_dir = Path("data/1_processed")
    geih_path = processed_dir / "geih_procesado.parquet"
    sisben_path = processed_dir / "sisben_iv_procesado.parquet"

    if not geih_path.exists() or not sisben_path.exists():
        logger.warning(
            "Faltan archivos procesados (%s / %s). Este script corre después "
            "de 3_preprocesamiento.py, cuando ambas fuentes estén vinculadas.",
            geih_path,
            sisben_path,
        )
        return

    df_geih = pd.read_parquet(geih_path)
    df_sisben = pd.read_parquet(sisben_path)

    resultado = validar_doble_conteo(df_geih, df_sisben)

    out_dir = Path("docs/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "validacion_linkage_geih_sisben.csv"
    resultado.to_csv(out_csv, index=False)

    total_naiva = resultado["suma_naiva"].sum()
    total_union = resultado["union_verdadera"].sum()
    total_doble = resultado["doble_conteo"].sum()
    pct = (total_doble / total_naiva * 100) if total_naiva else 0.0

    print(f"Suma naíve (GEIH + Sisbén IV): {total_naiva:,.0f}")
    print(f"Unión verdadera (hogares únicos): {total_union:,.0f}")
    print(f"Doble conteo evitado: {total_doble:,.0f} ({pct:.1f}%)")
    print(f"Detalle guardado en: {out_csv}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
