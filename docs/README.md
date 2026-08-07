# Carpeta: docs (Documentación)
---
Este directorio consolida toda la documentación del proyecto, en formatos
legibles tanto para audiencias técnicas como no técnicas.

## Contenido y artefactos

### Documentos fundamentales
- **[`DICCIONARIO_DATOS.md`](DICCIONARIO_DATOS.md)**
  - Diccionario de datos consolidado: variables efectivamente en uso
    (identificadores, outcome, predictoras, tratamiento pendiente),
    tipo, distribución real y estado por fuente. Se actualiza cada vez
    que se integra una fuente nueva.
- **[`Anteproyecto_Sisben_IV.docx`](Anteproyecto_Sisben_IV.docx)**
  - Documento formal de anteproyecto (abril 2026): introducción, marco
    teórico, revisión de literatura, objetivos general y específicos
    (OE1–OE5), metodología, población y muestra, fases de desarrollo,
    cronograma y bibliografía.
- **`DAG_causal.md` / `.png`** *(pendiente)*
  - Diagrama causal (DAG) propuesto: tratamiento (clasificación Sisbén
    IV), outcome (bienestar multidimensional), confusores y mediadores.
  - Justificación de cada arista con literatura o razonamiento experto.
- **`Supuestos_de_identificacion.md`** *(pendiente)*
  - Criterios evaluados (backdoor, RDD) y supuestos asumidos
    explícitamente (ignorabilidad condicional, positividad, SUTVA).

### Subcarpeta `img/`
- Recursos visuales: DAGs, diagramas de flujo ETL, gráficos exportados
  desde los notebooks.

### Subcarpeta `reports/`
- **`Reporte_EDA.pdf`** *(pendiente, Fase 2)*: hallazgos del análisis
  exploratorio por fuente y subpoblación.
- **`Reporte_Determinantes_Puntaje.pdf`** *(pendiente, OE1)*: resultados
  LASSO/Ridge y SHAP sobre el puntaje Sisbén IV.
- **`Reporte_Suficiencia_Explicativa.pdf`** *(pendiente, OE2)*: AUC-ROC,
  RMSE y análisis de residuales frente a la pobreza latente.
- **`Reporte_Resultados_Causales.pdf`** *(pendiente, OE3)*: ATE, CATE,
  test BLP (Causal Forest / DML).
- **`Informe_Final_Ejecutivo.pdf`** *(pendiente, OE5)*: comparación FGT1
  y recomendaciones de política pública.
