
# Proyecto: Inferencia causal sobre la clasificación en el Sisbén IV
---
![Logo Universidad Santo Tomás](https://usantotomas.edu.co/hs-fs/hubfs/social-suggested-images/usantotomas.edu.cohs-fshubfsLogo%20Santoto%20-%20SP%20Bogota%20Horizontal%20blanco-2.png)

## Consultorio de Estadística y Ciencia de Datos
**Universidad Santo Tomás — Facultad de Ingeniería — Maestría en Ciencia de Datos**

- **Estudiantes**: Juan Sebastián Fonseca Arévalo, José Mateo Roncancio Marín
- **Profesor**: Carlos Isaac Zainea Maya
- **Año**: 2026

### 1. Descripción General

Este repositorio contiene los artefactos y el código del proyecto de grado
**"Efecto causal del Sisbén IV en la identificación de la pobreza y el
bienestar multidimensional en hogares colombianos"**. El proyecto evalúa
el efecto causal de la clasificación del Sisbén IV sobre el bienestar
multidimensional de hogares colombianos, mediante técnicas de **Causal
Forest** y **Double Machine Learning (DML)**, integrando fuentes GEIH,
Sisbén IV, DPS, IPM y RUI.

A diferencia de un enfoque puramente predictivo, el proyecto se centra en
**inferencia causal**: estimar el efecto de la clasificación Sisbén IV
sobre indicadores de bienestar real, bajo supuestos de identificación
explícitos, con el fin de entender las causas estructurales detrás de los
errores de inclusión y exclusión reportados (DNP-BID, 2022).

La estructura sigue la metodología estandarizada del **Consultorio de
Estadística y Ciencia de Datos** de la USTA, garantizando reproducibilidad,
colaboración y calidad en cada fase del ciclo de vida del proyecto.

### 2. Pregunta de investigación y objetivos

**Objetivo general:** evaluar el efecto causal de la clasificación del
Sisbén IV sobre la condición real de pobreza de los hogares colombianos en
2026, comparando su poder de focalización con las mediciones del DANE, el
DNP y el RUI.

**Objetivos específicos:**
- **OE1.** Identificar y ponderar las variables que determinan el puntaje
  Sisbén IV (LASSO/Ridge, SHAP values).
- **OE2.** Evaluar la suficiencia explicativa del Sisbén IV frente a la
  pobreza latente (GEIH, IPM, RUI).
- **OE3.** Estimar el efecto causal heterogéneo del Sisbén IV sobre el
  bienestar del hogar (Causal Forest, DML — ATE, CATE).
- **OE4.** Diseñar e implementar la integración de fuentes administrativas
  y de encuesta (GEIH, Sisbén IV, DPS, IPM, RUI).
- **OE5.** Comparar el modelo cuantílico del Sisbén IV frente a los
  enfoques causales (brecha de pobreza FGT1, errores de focalización).

Detalle completo de marco teórico, metodología y cronograma en
[`docs/Anteproyecto_Sisben_IV.docx`](docs/Anteproyecto_Sisben_IV.docx).

### 3. Stack tecnológico

![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)

- **Lenguaje principal**: Python 3.12
- **Gestor de dependencias**: Poetry
- **Librerías centrales**:
  - Manipulación de datos: `pandas`, `numpy`, `pyarrow`
  - Modelado ML base: `scikit-learn`, `xgboost`
  - Inferencia causal: `dowhy`, `econml`, `causal-learn`, `networkx`
  - Interpretabilidad: `shap`
  - Visualización: `matplotlib`, `seaborn`, `graphviz`
  - Entorno exploratorio: `jupyterlab`

### 4. Cómo empezar

1. **Clona el repositorio**:
    ```bash
    git clone <url-del-repo>
    cd sisben_causal
    ```

2. **Instala las dependencias con Poetry**:
    ```bash
    poetry install
    ```

3. **Activa el entorno virtual**:
    ```bash
    poetry shell
    ```

4. **Configura las credenciales de fuentes abiertas** (Socrata/DANE):
    ```bash
    cp .env.example .env
    # completar SOCRATA_APP_TOKEN si se dispone de uno (opcional, aumenta el rate limit)
    ```

5. **Lanza Jupyter para explorar los notebooks**:
    ```bash
    jupyter lab
    ```

### 5. Estructura del repositorio

- **`/data`**: Datos en sus tres estados (`0_raw`, `1_processed`, `2_models`)
  y el catálogo de fuentes ([`data/catalogo.yaml`](data/catalogo.yaml)).
  Los microdatos del Sisbén y GEIH **no se versionan**; ver `.gitignore`.
- **`/docs`**: Documentación del proyecto — anteproyecto, DAG causal,
  informes, reportes y el
  [**diccionario de datos**](docs/DICCIONARIO_DATOS.md) (variables en uso,
  tipos, distribución y estado por fuente).
- **`/notebooks`**: Cuadernos de exploración, prototipado de DAGs y
  pruebas de identificación.
- **`/src`**: Código fuente de producción (ETL, limpieza, preprocesamiento,
  especificación causal, estimación, refutación).
- **`.gitignore`**: Exclusiones de control de versiones (datos sensibles,
  entornos, modelos pesados).
- **`pyproject.toml`**: Configuración del proyecto gestionado por Poetry.
- **`README.md`**: Este archivo.

### 6. Flujo metodológico (resumen)

1. **Integración** de fuentes (Sisbén IV, GEIH, DPS, IPM, RUI).
2. **Limpieza** y armonización de variables entre fuentes.
3. **Preprocesamiento**: definición de tratamiento, outcome, confusores y
   pobreza latente.
4. **Especificación causal**: construcción del DAG y análisis de
   identificabilidad (backdoor, RDD).
5. **Estimación**: DML, Causal Forest (ATE, CATE, BLP).
6. **Refutación**: placebo, subset aleatorio, sensibilidad a confusores
   no observados.
7. **Reporte** de efectos y comparación FGT1 frente al modelo cuantílico.

Fases y cronograma detallado (abril 2026 – febrero 2027) en el anteproyecto,
sección 4.5 y 5.

### 7. Estado del proyecto

| Fase | Período | Estado |
|---|---|---|
| Fase 1 — Marco teórico y estado del arte | Abr–jun 2026 | ✅ Anteproyecto entregado |
| Fase 2 — Integración y limpieza de datos | Jun–ago 2026 | 🔧 En curso — estructura de repositorio y catálogo de fuentes |
| Fase 3 — OE1/OE2 (LASSO, SHAP, suficiencia) | Ago–sep 2026 | ⏳ Pendiente |
| Fase 4 — OE3/OE5 (DML, Causal Forest, RDD) | Sep–nov 2026 | ⏳ Pendiente |
| Fase 5 — Redacción y entrega final | Nov 2026–feb 2027 | ⏳ Pendiente |

### 8. Consideraciones éticas y de datos

- Los datos individuales del Sisbén IV son **sensibles**; se trabajará
  con versiones anonimizadas o agregadas conforme a las políticas del DNP
  y la normativa de protección de datos (Ley 1581 de 2012).
- Ninguna base con información personal debe subirse al repositorio.
- Los resultados son de naturaleza académica y no constituyen una
  evaluación oficial del Sisbén IV.

### 9. Créditos y referencia metodológica

El patrón de arquitectura de datos (capas de ingesta, catálogo de fuentes
versionado y trazabilidad de transformaciones) se basa en el enfoque
empleado en el proyecto hermano del Consultorio, *Sinergia socioeconómica:
contratación pública, estructura territorial y economía popular*
(repositorio `desarrollo_social_y_economico`), adaptado aquí a fuentes de
registro social (GEIH, Sisbén IV, DPS, IPM, RUI).
