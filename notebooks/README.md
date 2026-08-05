# Carpeta: notebooks
---
Cuadernos de Jupyter para la exploración interactiva, el prototipado
del DAG causal y la validación de estimadores.

## Propósito y artefactos

### 1. Exploración y descubrimiento
- Carga inicial de fuentes (GEIH, Sisbén IV, DPS, IPM, RUI).
- Descripción por subpoblación (víctimas, étnicos, rurales dispersos).
- Validación de cobertura y calidad de variables candidatas a
  confusores.

### 2. Prototipado causal
- Construcción iterativa del DAG.
- Pruebas de identificación (backdoor, RDD en torno a los umbrales del
  puntaje Sisbén IV).
- Ensayos de estimadores (DML, Causal Forest).
- Refutación: placebo, random common cause, subset aleatorio,
  sensibilidad.

## Nomenclatura sugerida

- `01_exploracion_fuentes.ipynb`
- `02_calidad_variables_confusoras.ipynb`
- `03_prototipo_dag.ipynb`
- `04_oe1_lasso_shap.ipynb`
- `05_oe2_suficiencia_explicativa.ipynb`
- `06_oe3_dml_causal_forest.ipynb`
- `07_oe5_comparacion_fgt1.ipynb`

## Buenas prácticas

- Un cuaderno debe contar una historia coherente, de principio a fin.
- Cuando una función se estabilice, **refactorízala a un módulo dentro
  de `/src`** para hacerla reutilizable y testeable.
- No dejes rutas absolutas dentro del cuaderno; usa rutas relativas o
  el archivo `data/catalogo.yaml`.
