# Diccionario de Datos — Proyecto Sisbén IV / Inferencia Causal

Este documento consolida las variables **efectivamente en uso** en el
proyecto (no el listado bruto de cada fuente). Para el diccionario
completo del IPM (146 variables originales del DDI de DANE), ver
[`data/diccionario_ipm_2025.md`](../data/diccionario_ipm_2025.md).

Estado general de fuentes: ver [`data/catalogo.yaml`](../data/catalogo.yaml).

---

## 1. Identificadores y ponderadores (IPM)

| Variable | Tipo | Descripción | Fuente | Notas |
|---|---|---|---|---|
| `DIRECTORIO` | string | Identificador del segmento muestral | IPM (DANE) | **No es único por hogar** — ver llave compuesta abajo |
| `SECUENCIA_ENCUESTA` | string | Secuencia de la encuesta dentro del segmento | IPM (DANE) | |
| `SECUENCIA_P` | string | Secuencia del hogar dentro de la encuesta | IPM (DANE) | |
| `FEX_C` | float64 | Factor de expansión a nivel hogar | IPM (DANE) | Usar siempre que se reporten cifras poblacionales, no solo conteos de muestra |
| `FEXP` | float64 | Factor de expansión a nivel personas | IPM (DANE) | |
| `PERSONAS` | float64 | Número de personas en el hogar | IPM (DANE) | |

> **Llave única de hogar:** `DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P`
> (0 duplicados verificado). `DIRECTORIO` solo tiene 212 duplicados en la
> base nacional porque identifica el segmento, no el hogar.

---

## 2. Variables de resultado (outcome) — bienestar real del hogar

| Variable | Tipo | Descripción | Distribución real (Hogares Nacional, n=79.125) |
|---|---|---|---|
| `IPM` | float64 (Int8 en privaciones) | Índice de Pobreza Multidimensional, suma ponderada de 15 privaciones | Media 0.195, rango [0.0, 0.86] |
| `POBRE` | Int8 (binaria 0/1) | Hogar clasificado como pobre (IPM ≥ 5/15) | 13.0% positivos (pobre), 87.0% negativos |

---

## 3. Variables predictoras — las 15 privaciones del IPM (Alkire-Foster)

Todas son binarias (`Int8`, 0=no privado / 1=privado), 0% de faltantes.

| Dimensión | Variable | Descripción |
|---|---|---|
| Educación | `logro_educativo` | Privación por bajo logro educativo |
| Educación | `analfabetismo` | Privación por analfabetismo |
| Educación | `inasistencia_escolar` | Privación por inasistencia escolar |
| Educación | `rezago_escolar` | Privación por rezago escolar |
| Niñez y juventud | `atencion_integral` | Barreras de acceso a atención integral primera infancia |
| Niñez y juventud | `trabajo_infantil` | Privación por trabajo infantil |
| Trabajo | `desempleo_larga_duracion` | Privación por desempleo de larga duración |
| Trabajo | `empleo_formal` | Privación por informalidad laboral |
| Salud | `aseguramiento_salud` | Privación por no aseguramiento en salud |
| Salud | `barreras_acceso_salud` | Barreras de acceso a salud dada una necesidad |
| Vivienda | `acueducto` | Sin acceso a fuente de agua mejorada |
| Vivienda | `alcantarillado` | Inadecuada eliminación de excretas |
| Vivienda | `pisos` | Material inadecuado de pisos |
| Vivienda | `paredes` | Material inadecuado de paredes exteriores |
| Vivienda | `hacinamiento` | Hacinamiento crítico |

---

## 4. Variables excluidas del análisis principal (módulo de submuestra)

| Variable | % Faltante | Motivo de exclusión |
|---|---|---|
| `PERIODO` | 77.79% | Módulo aplicado solo a una submuestra (missing por diseño, no por hogar) |
| `P1075` | 77.79% | Ídem |
| `P1077S21` | 77.79% | Ídem |
| `P1077S22` | 77.79% | Ídem |
| `P1077S23` | 77.79% | Ídem |

Se conservan como `NaN` explícito en `data/1_processed/`, sin imputar —
ver justificación completa en
[`docs/reports/reporte_faltantes_ipm_hogares.csv`](reports/reporte_faltantes_ipm_hogares.csv).

---

## 5. Variable de tratamiento — pendiente

| Variable | Tipo esperado | Fuente | Estado |
|---|---|---|---|
| `puntaje_sisben` | float (0-100) | Sisbén IV (DNP) | ⏳ Solicitud enviada, pendiente de respuesta |
| `grupo_elegibilidad` | categórica (A/B/C/D) | Sisbén IV (DNP) | ⏳ Solicitud enviada, pendiente de respuesta |

---

## 6. Variables previstas de otras fuentes (aún no integradas)

| Fuente | Variables previstas | Estado |
|---|---|---|
| GEIH (DANE) | ingreso per cápita, condición de ocupación, informalidad laboral, composición del hogar | ⏳ Registro ANDA en trámite |
| DPS | beneficiario Familias en Acción, beneficiario Ingreso Solidario | ⏳ Solicitud no enviada aún |
| RUI (UARIV) | condición de víctima del conflicto armado | ⏳ Solicitud no enviada aún |

---

*Última actualización: procesamiento de IPM Hogares Nacional 2025
(`src/2_limpieza.py`). Actualizar esta tabla cada vez que se integre una
fuente nueva o se agregue una variable al análisis.*
