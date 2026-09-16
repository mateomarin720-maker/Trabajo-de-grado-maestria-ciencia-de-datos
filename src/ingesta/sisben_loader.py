"""Loader de Sisbén IV 2024 (muestra anonimizada ANDA-DNP, catálogo 168).

Procesa las 3 tablas descargadas de https://anda.dnp.gov.co/index.php/catalog/168:
    SISBEN_Hog_SIV_2024.txt   (1.833.166 hogares, 33 variables)
    SISBEN_Pers_SIV_2024.txt  (4.715.226 personas, 48 variables)
    SISBEN_Viv_SIV_2024.txt   (1.699.927 viviendas, 15 variables)

Formato de origen: texto plano separado por tabulador (\t), UTF-8/ASCII
(confirmado 2026-08-09 con chardet — no requiere latin1 como GEIH).

Estructura esperada en disco (misma convención de data/0_raw/ que el
resto del proyecto — NO se versiona en git, ver .gitignore):

    data/0_raw/sisben_iv/2024/SISBEN_Hog_SIV_2024.txt
    data/0_raw/sisben_iv/2024/SISBEN_Pers_SIV_2024.txt
    data/0_raw/sisben_iv/2024/SISBEN_Viv_SIV_2024.txt

Llave de hogar: cod_mpio + zona + llave + corte (+ hogar en Viviendas
cuando aplica, ya que una vivienda puede tener varios hogares).
Llave de persona: se agrega ORDEN a la llave de hogar.

⚠️ IMPORTANTE — llave NO compatible con GEIH/IPM: el campo `llave` aquí
es un consecutivo local por municipio/zona (0001, 0002...), no un
identificador nacional único como DIRECTORIO de DANE. Por diseño, no
existe join directo posible con GEIH/IPM — esto confirma que Hot-Deck
(fusión estadística) es la vía correcta, no un problema a resolver.

⚠️ IMPORTANTE — circularidad: las columnas I1-I15 y H_5 en Personas son
la versión propia de Sisbén de las 15 privaciones Alkire-Foster / IPM
proxy. NUNCA usar estas columnas como Outcome del análisis causal — el
algoritmo Sisbén ya las incorpora, así que usarlas como resultado sería
medir el algoritmo con su propia regla (ver docs/DICCIONARIO_HOTDECK.md).

Uso:
    poetry run python -m src.ingesta.sisben_loader
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = Path("data/0_raw/sisben_iv/2024")
OUT_DIR = Path("data/1_processed/sisben_iv/2024")

CHUNK_SIZE = 200_000

ARCHIVOS = {
    "hogares": "SISBEN_Hog_SIV_2024.txt",
    "personas": "SISBEN_Pers_SIV_2024.txt",
    "viviendas": "SISBEN_Viv_SIV_2024.txt",
}

# Columnas de privación proxy en Personas que NUNCA deben usarse como
# Outcome (ver advertencia de circularidad en el docstring del módulo).
COLUMNAS_PROXY_CIRCULARES = [f"I{i}" for i in range(1, 16)] + ["H_5"]


def _parse_txt_a_parquet(input_path: Path, output_path: Path, nombre_tabla: str) -> dict[str, Any]:
    """Convierte un TXT separado por tabulador a Parquet, por chunks.

    Todo se lee como string (capa raw, sin tipar — igual que el resto
    del pipeline). Agrega metadatos de trazabilidad estándar del proyecto.
    """
    if not input_path.exists():
        msg = f"Archivo no encontrado: {input_path}"
        logger.error(msg)
        return {"status": "error", "error": msg}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Leyendo %s (%.2f GB)", input_path, input_path.stat().st_size / (1024**3))

    writer = None
    total = 0
    try:
        for chunk in pd.read_csv(
            input_path,
            sep="\t",
            dtype=str,
            keep_default_na=False,
            low_memory=False,
            encoding="utf-8",
            on_bad_lines="warn",
            chunksize=CHUNK_SIZE,
        ):
            if chunk.empty:
                continue
            chunk["_ingestion_timestamp"] = datetime.now().isoformat()
            chunk["_source"] = "sisben_iv"
            chunk["_source_file"] = input_path.name

            table = pa.Table.from_pandas(chunk)
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema)
            writer.write_table(table)
            total += len(chunk)
    finally:
        if writer is not None:
            writer.close()

    logger.info("  %s: %s filas -> %s", nombre_tabla, f"{total:,}", output_path)
    return {"status": "success", "rows": total, "output": str(output_path)}


def ingest_sisben() -> dict[str, dict]:
    """Procesa las 3 tablas de Sisbén IV 2024 disponibles en data/0_raw/."""
    resumen = {}
    for nombre, archivo in ARCHIVOS.items():
        input_path = RAW_DIR / archivo
        output_path = OUT_DIR / f"{nombre}.parquet"
        resumen[nombre] = _parse_txt_a_parquet(input_path, output_path, nombre)
    return resumen


def main() -> None:
    resumen = ingest_sisben()
    print("\n=== Resumen Sisbén IV 2024 ===")
    for nombre, r in resumen.items():
        if r["status"] == "success":
            print(f"{nombre}: {r['rows']:,} filas -> {r['output']}")
        else:
            print(f"{nombre}: ERROR — {r['error']}")


if __name__ == "__main__":
    main()
