"""
Ingesta de microdatos locales (CSV) hacia data/0_raw/, por lotes (chunks).

Adaptado del patrón usado en el repo de referencia
`desarrollo_social_y_economico` (`src/ingesta/bronze/parsers/parser_csv_secop.py`
y `parser_csv_cnpv.py`, rama `trabajo-final`) para las fuentes de acceso
restringido de este proyecto: GEIH y Sisbén IV llegan como archivos CSV
locales (entregados por DANE/DNP tras la solicitud institucional, no vía
API), a veces muy pesados o repartidos en varios archivos (p. ej. por
departamento o por mes). Leer todo con `pd.read_csv` de una sola vez puede
saturar la RAM — este módulo lee por chunks y escribe directo a Parquet.

Uso típico, un solo archivo (p. ej. Sisbén IV entregado como CSV único):

    from src.ingesta.local_csv_parser import parse_csv_a_parquet

    parse_csv_a_parquet(
        input_path="data/0_raw/sisben_iv/sisben_iv_bruto.csv",
        output_path="data/0_raw/sisben_iv/sisben_iv.parquet",
        fuente_id="sisben_iv",
    )

Uso típico, varios archivos en una carpeta (p. ej. GEIH por mes o depto):

    from src.ingesta.local_csv_parser import parse_carpeta_csv_a_parquet

    parse_carpeta_csv_a_parquet(
        input_dir="data/0_raw/geih/crudos/",
        output_path="data/0_raw/geih/geih.parquet",
        fuente_id="geih",
    )
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 250_000


def _detectar_separador(csv_path: Path) -> str:
    """Detecta si el CSV usa ';' o ',' leyendo la primera línea."""
    with open(csv_path, encoding="utf-8", errors="ignore") as f:
        primera_linea = f.readline()
    return ";" if ";" in primera_linea else ","


def parse_csv_a_parquet(
    input_path: str | Path,
    output_path: str | Path,
    fuente_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict[str, Any]:
    """Convierte un único CSV (potencialmente pesado) a Parquet, por chunks.

    Todos los campos se leen como string (capa raw = datos crudos, sin
    tipado todavía — eso se hace en `2_limpieza.py`). Agrega metadatos de
    trazabilidad (`_ingestion_timestamp`, `_source`, `_source_file`) a
    cada fila, igual que en el pipeline de referencia.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        msg = f"Archivo no encontrado: {input_path}"
        logger.error(msg)
        return {"status": "error", "error": msg}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sep = _detectar_separador(input_path)

    logger.info(
        "Leyendo %s (%.2f GB, sep='%s')",
        input_path,
        input_path.stat().st_size / (1024**3),
        sep,
    )

    writer = None
    total_records = 0
    try:
        for i, chunk in enumerate(
            pd.read_csv(
                input_path,
                chunksize=chunk_size,
                sep=sep,
                dtype=str,
                keep_default_na=False,
                low_memory=False,
                encoding="utf-8",
                on_bad_lines="warn",
            )
        ):
            if chunk.empty:
                continue

            chunk["_ingestion_timestamp"] = datetime.now().isoformat()
            chunk["_source"] = fuente_id
            chunk["_source_file"] = input_path.name

            table = pa.Table.from_pandas(chunk)
            if writer is None:
                writer = pq.ParquetWriter(output_path, table.schema, compression="snappy")
            writer.write_table(table)
            total_records += len(chunk)

            if (i + 1) % 10 == 0:
                logger.info("  chunk %s — %s filas acumuladas", i + 1, f"{total_records:,}")

    finally:
        if writer:
            writer.close()

    if total_records == 0:
        logger.warning("No se escribió nada — ¿archivo vacío?: %s", input_path)
        return {"status": "warning", "error": "Archivo vacío", "archivo": str(input_path)}

    logger.info("Guardado: %s (%s filas)", output_path, f"{total_records:,}")
    return {
        "status": "success",
        "archivo": str(output_path),
        "registros": total_records,
        "fuente": fuente_id,
    }


def parse_carpeta_csv_a_parquet(
    input_dir: str | Path,
    output_path: str | Path,
    fuente_id: str,
    patron: str = "*.csv",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict[str, Any]:
    """Consolida varios CSV de una carpeta (p. ej. GEIH por mes/departamento)
    en un único Parquet, leyendo cada archivo por chunks.
    """
    input_dir = Path(input_dir)
    output_path = Path(output_path)

    if not input_dir.exists() or not input_dir.is_dir():
        msg = f"Carpeta no encontrada: {input_dir}"
        logger.error(msg)
        return {"status": "error", "error": msg}

    archivos = sorted(input_dir.glob(patron))
    if not archivos:
        msg = f"No se encontraron archivos '{patron}' en {input_dir}"
        logger.error(msg)
        return {"status": "error", "error": msg}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Consolidando %s archivos de %s", len(archivos), input_dir)

    writer = None
    total_records = 0
    archivos_ok, archivos_error = 0, 0

    for csv_file in archivos:
        try:
            sep = _detectar_separador(csv_file)
            for chunk in pd.read_csv(
                csv_file,
                chunksize=chunk_size,
                sep=sep,
                dtype=str,
                keep_default_na=False,
                low_memory=False,
                on_bad_lines="skip",
            ):
                if chunk.empty:
                    continue
                chunk["_ingestion_timestamp"] = datetime.now().isoformat()
                chunk["_source"] = fuente_id
                chunk["_source_file"] = csv_file.name

                table = pa.Table.from_pandas(chunk)
                if writer is None:
                    writer = pq.ParquetWriter(output_path, table.schema, compression="snappy")
                writer.write_table(table)
                total_records += len(chunk)
            archivos_ok += 1
            logger.info("  OK: %s", csv_file.name)
        except Exception as e:  # noqa: BLE001 — se documenta y se continúa con el resto
            archivos_error += 1
            logger.error("  Error en %s: %s", csv_file.name, e)

    if writer:
        writer.close()

    logger.info(
        "Consolidación completa: %s archivos OK, %s con error, %s filas",
        archivos_ok,
        archivos_error,
        f"{total_records:,}",
    )
    return {
        "status": "success" if total_records > 0 else "error",
        "archivo": str(output_path),
        "registros": total_records,
        "archivos_procesados": archivos_ok,
        "archivos_con_error": archivos_error,
        "fuente": fuente_id,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(
        "Módulo de ingesta local. Importar parse_csv_a_parquet o "
        "parse_carpeta_csv_a_parquet desde 1_integracion.py una vez se "
        "tenga el microdato de GEIH o Sisbén IV depositado en data/0_raw/."
    )
