"""
Validador de integridad, representatividad y error muestral de GEIH 2024.

Corre después de `src.ingesta.geih_loader` (o `1_integracion.py`, que lo
invoca). Es el mismo tipo de chequeo de calidad ya hecho para IPM en
`2_limpieza.py` (duplicados, % de faltantes), más dos cosas específicas de
una encuesta con factor de expansión: cobertura departamental estable mes
a mes, y una primera aproximación al error muestral usando FEX_C18.

Uso:
    poetry run python -m src.utils.validar_geih

⚠️ Limitación importante sobre el error muestral: el microdato PÚBLICO de
GEIH no trae las variables de diseño (estrato de muestreo, UPM/conglomerado)
que permitirían un cálculo de varianza por linealización de Taylor como el
que usa DANE internamente. Lo que se reporta aquí (`reporte_error_muestral_geih.csv`)
es un error "naíve" bajo supuesto de muestreo aleatorio simple (SRS) sobre
los hogares de cada mes — es una COTA INFERIOR del error real: el diseño
complejo de GEIH (estratificado + conglomerado) típicamente tiene un efecto
de diseño (deff) > 1, así que el error real es mayor al aquí reportado. Para
el error oficial, usar el error estándar publicado por DANE en sus anexos de
indicadores, o solicitar las variables de diseño en la petición ANDA.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/1_processed/geih/2024")
REPORT_DIR = Path("docs/reports")

MODULOS = [
    "hogar_vivienda",
    "caracteristicas_generales",
    "fuerza_trabajo",
    "no_ocupados",
    "ocupados",
    "otras_formas_trabajo",
    "otros_ingresos",
    "migracion",
]
LLAVE_HOGAR = ["DIRECTORIO", "SECUENCIA_P", "HOGAR"]
N_DEPARTAMENTOS_ESPERADOS = 33  # ver nota en catalogo.yaml (incl. dominios especiales)


def _meses_disponibles() -> list[str]:
    if not PROCESSED_DIR.exists():
        return []
    return sorted(p.name for p in PROCESSED_DIR.iterdir() if p.is_dir())


def reporte_completitud() -> pd.DataFrame:
    """Matriz mes x módulo: filas, % de FEX_C18 faltante, formato de origen.

    `formato_origen` distingue los módulos recuperados vía fallback .DTA
    (ver `geih_loader.py`, caso agosto 2024) de los leídos directamente
    del CSV — trazabilidad necesaria porque el tipado difiere ligeramente
    entre ambos orígenes hasta que pasen por `2_limpieza.py`.
    """
    filas = []
    for mes in _meses_disponibles():
        for modulo in MODULOS:
            path = PROCESSED_DIR / mes / f"{modulo}.parquet"
            if not path.exists():
                filas.append(
                    {
                        "mes": mes,
                        "modulo": modulo,
                        "estado": "FALTANTE",
                        "filas": 0,
                        "pct_fex_c18_faltante": None,
                        "formato_origen": None,
                    }
                )
                continue

            df = pd.read_parquet(path)
            formato = (
                "dta_fallback"
                if "_source_format" in df.columns and (df["_source_format"] == "dta_fallback").any()
                else "csv"
            )
            pct_fex = None
            if "FEX_C18" in df.columns:
                fex_num = pd.to_numeric(df["FEX_C18"], errors="coerce")
                pct_fex = round(fex_num.isna().mean() * 100, 2)

            filas.append(
                {
                    "mes": mes,
                    "modulo": modulo,
                    "estado": "OK",
                    "filas": len(df),
                    "pct_fex_c18_faltante": pct_fex,
                    "formato_origen": formato,
                }
            )
    return pd.DataFrame(filas)


def reporte_duplicados_hogar() -> pd.DataFrame:
    """Duplicados de la llave de hogar (DIRECTORIO+SECUENCIA_P+HOGAR) por mes."""
    filas = []
    for mes in _meses_disponibles():
        path = PROCESSED_DIR / mes / "hogar_vivienda.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        faltan = set(LLAVE_HOGAR) - set(df.columns)
        if faltan:
            filas.append(
                {"mes": mes, "hogares": len(df), "duplicados": None, "nota": f"faltan columnas de llave: {faltan}"}
            )
            continue
        n_dup = int(df.duplicated(subset=LLAVE_HOGAR).sum())
        filas.append({"mes": mes, "hogares": len(df), "duplicados": n_dup, "nota": ""})
    return pd.DataFrame(filas)


def reporte_representatividad_departamental() -> pd.DataFrame:
    """Cobertura de departamentos (DPTO) y tamaño de muestra por mes.

    Un mes con menos de 33 departamentos representados es una señal de
    posible sesgo de cobertura si se usa ese mes de forma aislada — no
    necesariamente un error (algunos dominios especiales rotan), pero se
    marca para revisión manual.
    """
    filas = []
    for mes in _meses_disponibles():
        path = PROCESSED_DIR / mes / "hogar_vivienda.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        if "DPTO" not in df.columns:
            continue
        n_dptos = df["DPTO"].nunique()
        filas.append(
            {
                "mes": mes,
                "n_departamentos": n_dptos,
                "cobertura_completa": n_dptos >= N_DEPARTAMENTOS_ESPERADOS,
                "hogares_muestra": len(df),
            }
        )
    return pd.DataFrame(filas)


def reporte_error_muestral() -> pd.DataFrame:
    """Error naíve (SRS) por mes para la proporción de hogares en cabecera
    municipal (CLASE=1), como indicador demostrativo de la magnitud mínima
    del error de muestreo esperable.

    NO es el error de diseño complejo real de GEIH — ver limitación en el
    docstring del módulo. `hogares_expandidos` (suma de FEX_C18) sirve
    además como chequeo de estabilidad: el total nacional de hogares no
    debería variar de forma brusca de un mes a otro.
    """
    filas = []
    for mes in _meses_disponibles():
        path = PROCESSED_DIR / mes / "hogar_vivienda.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        if not {"CLASE", "FEX_C18"}.issubset(df.columns):
            continue

        fex = pd.to_numeric(df["FEX_C18"], errors="coerce")
        es_cabecera = (df["CLASE"] == "1").astype(float)
        valido = fex.notna()

        n = int(valido.sum())
        poblacion_expandida = fex[valido].sum()
        p_ponderado = (es_cabecera[valido] * fex[valido]).sum() / poblacion_expandida
        se_srs = np.sqrt(p_ponderado * (1 - p_ponderado) / n)
        ic95_bajo = max(0.0, p_ponderado - 1.96 * se_srs)
        ic95_alto = min(1.0, p_ponderado + 1.96 * se_srs)

        filas.append(
            {
                "mes": mes,
                "n_hogares_muestra": n,
                "hogares_expandidos": round(poblacion_expandida),
                "pct_cabecera_ponderado": round(p_ponderado * 100, 2),
                "error_estandar_naive_srs_pct": round(se_srs * 100, 3),
                "ic95_bajo_pct": round(ic95_bajo * 100, 2),
                "ic95_alto_pct": round(ic95_alto * 100, 2),
            }
        )
    return pd.DataFrame(filas)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    meses = _meses_disponibles()

    completitud = reporte_completitud()
    completitud.to_csv(REPORT_DIR / "reporte_completitud_geih.csv", index=False)

    duplicados = reporte_duplicados_hogar()
    duplicados.to_csv(REPORT_DIR / "reporte_duplicados_geih.csv", index=False)

    representatividad = reporte_representatividad_departamental()
    representatividad.to_csv(REPORT_DIR / "reporte_representatividad_geih.csv", index=False)

    error_muestral = reporte_error_muestral()
    error_muestral.to_csv(REPORT_DIR / "reporte_error_muestral_geih.csv", index=False)

    print("=== Validación GEIH 2024 ===\n")
    print(f"Meses con datos en 1_processed/: {len(meses)}/12 ({', '.join(meses) if meses else 'ninguno'})")

    faltantes = completitud[completitud["estado"] == "FALTANTE"]
    print(f"Módulos faltantes: {len(faltantes)}")
    if len(faltantes):
        print(faltantes[["mes", "modulo"]].to_string(index=False))

    dta = completitud[completitud["formato_origen"] == "dta_fallback"]
    if len(dta):
        print(f"\nMódulos recuperados vía fallback .DTA (CSV incompleto en origen): {len(dta)}")
        print(dta[["mes", "modulo"]].to_string(index=False))

    total_dup = duplicados["duplicados"].sum() if len(duplicados) else 0
    print(f"\nDuplicados de llave hogar (DIRECTORIO+SECUENCIA_P+HOGAR): {total_dup} (esperado: 0)")

    if len(representatividad):
        incompletos = representatividad[~representatividad["cobertura_completa"]]
        print(
            f"Meses con cobertura departamental < {N_DEPARTAMENTOS_ESPERADOS}: "
            f"{len(incompletos)}"
            + (f" ({', '.join(incompletos['mes'])})" if len(incompletos) else "")
        )

    if len(error_muestral):
        print("\nEstabilidad de hogares expandidos (FEX_C18) por mes:")
        print(error_muestral[["mes", "hogares_expandidos", "pct_cabecera_ponderado", "ic95_bajo_pct", "ic95_alto_pct"]].to_string(index=False))

    print(f"\nReportes guardados en {REPORT_DIR}/:")
    print("  - reporte_completitud_geih.csv")
    print("  - reporte_duplicados_geih.csv")
    print("  - reporte_representatividad_geih.csv")
    print("  - reporte_error_muestral_geih.csv")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
