# src/ingesta

Módulos de conexión a fuentes de datos.

- **`socrata_client.py`**: cliente genérico para portales Socrata (fuentes
  con `acceso: abierto` en `data/catalogo.yaml`, p. ej. indicadores
  agregados de IPM en datos.gov.co). Paginación automática, guardado
  directo a `data/0_raw/` en parquet.

- **`local_csv_parser.py`**: ingesta de microdatos locales (CSV) por
  chunks — para GEIH y Sisbén IV, que llegan como archivos entregados
  directamente por DANE/DNP (no vía API), a veces pesados o repartidos en
  varios archivos por departamento/mes. Adaptado del patrón real usado en
  el repo de referencia `desarrollo_social_y_economico`
  (`src/ingesta/bronze/parsers/parser_csv_secop.py` y
  `parser_csv_cnpv.py`, rama `trabajo-final`), que lee CSV de hasta ~10GB
  por lotes con PyArrow en vez de cargarlos completos en RAM.
  - `parse_csv_a_parquet(...)`: para un solo archivo.
  - `parse_carpeta_csv_a_parquet(...)`: para varios archivos en una
    carpeta (p. ej. GEIH repartida por mes).

- **Fuentes de acceso restringido** (`solicitud_institucional` o
  `registro` en `data/catalogo.yaml`: Sisbén IV, DPS, RUI, GEIH
  microdato) **no tienen cliente API** — no existe endpoint público. El
  flujo es: (1) tramitar la solicitud ante la entidad correspondiente,
  (2) depositar el archivo entregado directamente en `data/0_raw/<fuente>/`,
  (3) correr `parse_csv_a_parquet` o `parse_carpeta_csv_a_parquet` sobre
  ese archivo/carpeta, (4) documentar la fecha y el canal de obtención en
  `data/catalogo.yaml` (campo `estado` → `disponible`).

## Próximos pasos (Fase 2 del cronograma, jun–ago 2026)

1. Tramitar registro GEIH (ANDA-DANE) y solicitud Sisbén IV (DNP).
2. Identificar el `dataset_id` Socrata exacto del IPM agregado en
   datos.gov.co y añadirlo a `data/catalogo.yaml` (`catalogo_ref`) — ya
   hecho para 2024/2025, ver catálogo.
3. Cuando llegue el microdato de GEIH o Sisbén IV, correr
   `local_csv_parser.py` sobre él desde `1_integracion.py`.
4. Escribir el conector de DPS/RUI en cuanto se defina el canal de
   entrega (API propia, SFTP o archivo plano).

