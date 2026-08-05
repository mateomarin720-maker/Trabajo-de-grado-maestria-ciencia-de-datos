# data/0_raw

Datos originales sin modificación alguna, tal como se obtienen de cada
fuente (GEIH, Sisbén IV, DPS, IPM, RUI). Ver [`../catalogo.yaml`](../catalogo.yaml)
para el detalle de cada fuente y su método de obtención.

**Regla de oro**: esta carpeta es de solo lectura. Ningún script debe
escribir aquí salvo los ingestores en `src/1_integracion.py` (o los módulos
en `src/ingesta/`). Toda transformación parte de una copia en
`data/1_processed/`.

Contenido no versionado por `.gitignore` (excepto este archivo).
