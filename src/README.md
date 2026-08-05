# Carpeta: src (Código fuente)
---
Contiene el código de producción del proyecto. A diferencia de los
notebooks, el código de esta carpeta debe ser modular, reutilizable,
documentado y preferiblemente cubierto por pruebas.

## Estructura y artefactos

- **`ingesta/`**
  - Módulos reutilizables de conexión a fuentes. `socrata_client.py`
    implementa un cliente genérico para portales Socrata (usado por
    `datos.gov.co` y `microdatos.dane.gov.co` para datasets abiertos como
    IPM agregado), siguiendo el mismo patrón de parsers Socrata + CSV del
    proyecto hermano `desarrollo_social_y_economico`.
  - Las fuentes de acceso restringido (Sisbén IV, DPS, RUI) no tienen
    cliente API — se documentan en `data/catalogo.yaml` como
    `solicitud_institucional` y se ingieren manualmente en `0_raw/` una
    vez obtenido el microdato.

- **`utils/`**
  - `config.py`: carga `data/catalogo.yaml` y variables de entorno
    (`.env`) de forma centralizada para todos los scripts.

- **`1_integracion.py`**
  - Script de integración de fuentes (ETL). Orquesta la ingesta de las
    fuentes abiertas vía `ingesta/socrata_client.py` y deja el resto de
    fuentes como placeholders documentados hasta que se resuelva el
    acceso institucional.

- **`2_limpieza.py`**
  - Limpieza y armonización: manejo de nulos, corrección de tipos,
    eliminación de duplicados, armonización de categorías entre fuentes.

- **`3_preprocesamiento.py`**
  - Construcción de variables: define explícitamente **tratamiento**
    (puntaje/grupo Sisbén IV), **outcomes** de bienestar, **pobreza
    latente** (GEIH+IPM+RUI) y **confusores**; codificación, escalado e
    imputación.

- **`4_dag_identificacion.py`**
  - Especificación del DAG causal y análisis de identificabilidad
    (backdoor, RDD en torno a los umbrales del puntaje).

- **`5_estimacion.py`**
  - Estimación de efectos causales: DML (ATE/LATE) y Causal Forest
    (CATE), test BLP de heterogeneidad (OE3).

- **`6_refutacion.py`**
  - Pruebas de refutación y sensibilidad: placebo, random common cause,
    data subset refuter, sensibilidad a confusores no observados.

- **`7_reporte/`**
  - Generación de reportes y visualizaciones reproducibles para
    `docs/reports/`, incluyendo la comparación FGT1 (OE5).

## Estándares de código

- **Modularidad**: funciones pequeñas con una única responsabilidad.
- **Documentación**: docstrings estilo Google o NumPy.
- **No hardcoding**: rutas y parámetros vienen de `data/catalogo.yaml`,
  `.env` o argumentos de CLI — nunca hardcodeados en el script.
- **Reproducibilidad**: fijar semillas aleatorias y registrar versiones
  de dependencias (`poetry.lock`).
