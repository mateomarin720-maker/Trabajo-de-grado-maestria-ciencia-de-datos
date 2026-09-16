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
| `ORDEN` | string | Orden de la persona dentro del hogar (solo tabla Personas) | IPM (DANE) | |
| `FEX_C` | float64 | Factor de expansión a nivel hogar | IPM (DANE) | Usar siempre que se reporten cifras poblacionales, no solo conteos de muestra |
| `FEXP` | float64 | Factor de expansión a nivel personas | IPM (DANE) | |
| `PERSONAS` | float64 | Número de personas en el hogar | IPM (DANE) | |

> **Llave única de hogar:** `DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P`
> (0 duplicados verificado). `DIRECTORIO` solo tiene 212 duplicados en la
> base nacional porque identifica el segmento, no el hogar.
> **Llave única de persona:** agrega `ORDEN` a la anterior.

---

## 1.b Modelo de datos — relación entre tablas ⚠️

El IPM se entrega en **3 tablas relacionadas** (Hogares / Personas /
Viviendas), cada una limpia de forma independiente en
`src/2_limpieza.py`:

| Tabla | Filas (nacional) | Llave única | Unida a Hogares? |
|---|---|---|---|
| Hogares | 79.125 | `DIRECTORIO+SECUENCIA_ENCUESTA+SECUENCIA_P` | — (es la base) |
| Personas | 212.617 | `DIRECTORIO+SECUENCIA_ENCUESTA+SECUENCIA_P+ORDEN` | ⚠️ **No todavía** |
| Viviendas | 78.913 | `DIRECTORIO+SECUENCIA_ENCUESTA+SECUENCIA_P` | ⚠️ **No todavía** |

**Pendiente de validar (verificado 2026-08-07):** el *join* de Personas
hacia Hogares usando la llave compuesta no cuadra de forma limpia — con
`DIRECTORIO+SECUENCIA_ENCUESTA` solamente aparecen 133.109 combinaciones
en Personas sin equivalente en Hogares. Puede deberse a que los 3
archivos de la descarga "nacional" no comparten exactamente el mismo
corte muestral, o a que `SECUENCIA_P` no tiene la misma semántica en
todas las tablas. **No se debe forzar el join** hasta confirmar con la
ficha metodológica de DANE (sección "método" del DDI) o soporte técnico
de ANDA. Mientras tanto, cada tabla se usa por separado.

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

## 3.b Variables de Personas (37 columnas, códigos DANE)

Todas son categóricas (códigos de respuesta), salvo `ORDEN` y `FEX_C`.
0% de faltantes salvo lo detallado en
[`docs/reports/reporte_faltantes_ipm_personas.csv`](reports/reporte_faltantes_ipm_personas.csv).

| Código | Etiqueta |
|---|---|
| `P6020` | Sexo |
| `P6040` | ¿Cuántos años cumplidos tiene? |
| `P6051` | Parentesco con el jefe/jefa del hogar |
| `P6090` | ¿Está afiliado a alguna EPS/ARS (incl. Sisbén)? |
| `P5665` | En últimos 30 días, ¿tuvo enfermedad/accidente/problema de salud? |
| `P8563` | ¿Qué hizo principalmente para tratar ese problema de salud? |
| `P51` | ¿Dónde permanece la mayor parte del tiempo entre semana? |
| `P55` | ¿Recibe desayuno/almuerzo donde permanece entre semana? |
| `P774` | ¿Paga por esa alimentación? |
| `P6160` | ¿Sabe leer y escribir? |
| `P8587` | ¿Actualmente estudia? |
| `P8587S1` | Nivel educativo más alto alcanzado / último grado aprobado |
| `P1088` | Grado o año aprobado |
| `P1088S1` | Nivel y grado en que está matriculado actualmente |
| `P6180` | Grado o año que cursa |
| `P6250` | ¿Recibe alimentación gratuita/subsidiada en el plantel? |
| `P6260` | Actividad principal la semana pasada |
| `P6270` | ¿Realizó alguna actividad paga adicional la semana pasada? |
| `P6351` | ¿Tenía trabajo/negocio aunque no trabajó la semana pasada? |
| `P7250` | ¿Trabajó sin pago en un negocio la semana pasada? |
| `P6920` | ¿Estaba disponible para trabajar la semana pasada? |
| `P8586` | ¿Durante cuántas semanas ha buscado trabajo? |
| `P3336S1` / `S2` / `S3` / `P3337` | Modalidad de estudio (presencial/virtual/alternancia) |
| `P6240` | ¿Tuvo comunicación con sus maestros la semana pasada? |
| `P1082S2` | ¿Tiene teléfono celular inteligente (smartphone)? |

## 3.c Variables de Viviendas (12 columnas)

| Código | Etiqueta |
|---|---|
| `P3` | Clase (cabecera/centro poblado/rural disperso) |
| `P4005` | Material predominante de las paredes exteriores |
| `P4015` | Material predominante de los pisos |
| `P8520S3` | Alcantarillado |
| `P8520S5` | Acueducto |
| `P5010` | ¿En cuántos cuartos duermen las personas del hogar? |
| `P8526` | Tipo de servicio sanitario |
| `P8530` | Principal fuente de agua para preparar alimentos |

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
