"""
Cliente genérico para portales de datos abiertos basados en Socrata
(p. ej. datos.gov.co, algunos catálogos de microdatos.dane.gov.co).

Adaptado del patrón de ingesta usado en el proyecto hermano
`desarrollo_social_y_economico` (parsers Socrata + CSV para SECOP/DANE),
generalizado aquí para cualquier dataset identificado por su `dataset_id`
(los 4x4 característicos de Socrata, p. ej. "f789-7hwg").

Uso típico:

    from src.ingesta.socrata_client import SocrataClient

    client = SocrataClient(domain="www.datos.gov.co")
    df = client.get_dataframe("f789-7hwg", where="anio=2024", limit=50000)
    client.save_raw(df, "data/0_raw/ipm/ipm_2024.parquet")

Requiere únicamente `requests` y `pandas`. El token de aplicación
(`SOCRATA_APP_TOKEN`) es opcional pero recomendable: sin él, el portal
aplica límites de tasa más estrictos.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 50_000


class SocrataClient:
    """Cliente mínimo para la API SODA de Socrata."""

    def __init__(self, domain: str, app_token: str | None = None) -> None:
        self.domain = domain.rstrip("/")
        self.app_token = app_token or os.getenv("SOCRATA_APP_TOKEN")
        self.session = requests.Session()
        if self.app_token:
            self.session.headers.update({"X-App-Token": self.app_token})

    def _endpoint(self, dataset_id: str) -> str:
        return f"https://{self.domain}/resource/{dataset_id}.json"

    def get_dataframe(
        self,
        dataset_id: str,
        where: str | None = None,
        select: str | None = None,
        limit: int | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> pd.DataFrame:
        """Descarga un dataset completo (o filtrado) paginando la API SODA.

        Args:
            dataset_id: identificador 4x4 del dataset en el portal Socrata.
            where: cláusula SoQL `$where` opcional (p. ej. "anio=2024").
            select: cláusula SoQL `$select` opcional (columnas a traer).
            limit: número máximo total de filas a traer (None = todas).
            page_size: tamaño de página por request (máx. recomendado 50000).

        Returns:
            DataFrame con todas las filas obtenidas.
        """
        rows: list[dict[str, Any]] = []
        offset = 0
        endpoint = self._endpoint(dataset_id)

        while True:
            remaining = None if limit is None else max(limit - len(rows), 0)
            if remaining == 0:
                break
            page_limit = page_size if remaining is None else min(page_size, remaining)

            params: dict[str, Any] = {"$limit": page_limit, "$offset": offset}
            if where:
                params["$where"] = where
            if select:
                params["$select"] = select

            logger.info(
                "Descargando %s — offset=%s limit=%s", dataset_id, offset, page_limit
            )
            resp = self.session.get(endpoint, params=params, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            page = resp.json()

            if not page:
                break
            rows.extend(page)
            offset += len(page)
            if len(page) < page_limit:
                break  # última página

        logger.info("Descarga completa: %s filas de %s", len(rows), dataset_id)
        return pd.DataFrame(rows)

    @staticmethod
    def save_raw(df: pd.DataFrame, path: str | Path) -> Path:
        """Guarda el DataFrame crudo en `data/0_raw/...` en formato parquet."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_path, index=False)
        logger.info("Guardado: %s (%s filas)", out_path, len(df))
        return out_path
