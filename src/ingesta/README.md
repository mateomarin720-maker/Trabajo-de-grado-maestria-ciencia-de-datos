# src/ingesta

Módulos de conexión a fuentes de datos.

- **`socrata_client.py`**: cliente genérico para portales Socrata (fuentes
  con `acceso: abierto` en `data/catalogo.yaml`, p. ej. indicadores
  agregados de IPM en datos.gov.co). Paginación automática, guardado
  directo a `data/0_raw/` en parquet.

- **Fuentes de acceso restringido** (`solicitud_institucional` o
  `registro` en `data/catalogo.yaml`: Sisbén IV, DPS, RUI, GEIH
  microdato) **no tienen cliente API** — no existe endpoint público. El
  flujo es: (1) tramitar la solicitud ante la entidad correspondiente,
  (2) depositar el archivo entregado directamente en `data/0_raw/<fuente>/`,
  (3) documentar la fecha y el canal de obtención en
  `data/catalogo.yaml` (campo `estado` → `disponible`).

## Próximos pasos (Fase 2 del cronograma, jun–ago 2026)

1. Tramitar registro GEIH (ANDA-DANE) y solicitud Sisbén IV (DNP).
2. Identificar el `dataset_id` Socrata exacto del IPM agregado en
   datos.gov.co y añadirlo a `data/catalogo.yaml` (`catalogo_ref`).
3. Escribir el conector de DPS/RUI en cuanto se defina el canal de
   entrega (API propia, SFTP o archivo plano).
