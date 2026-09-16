# Diccionario consolidado — Variables para Hot-Deck (GEIH ↔ Sisbén IV)

Este documento lista **únicamente** las variables que se usarán como
insumo de la fusión estadística (Hot-Deck) entre GEIH y Sisbén IV 2024 —
no es el diccionario completo de ninguna de las dos fuentes (ver
`docs/DICCIONARIO_DATOS.md` para el diccionario completo del IPM/GEIH).

Verificado contra el catálogo oficial ANDA-DNP (168):
https://anda.dnp.gov.co/index.php/catalog/168/data_dictionary

## 1. Variable de tratamiento (el hogar "donante" aporta esto)

| Variable Sisbén | Etiqueta | Notas |
|---|---|---|
| `Grupo` | Grupo (A/B/C/D) | Distribución real 2024: A=2.112.170, B=1.614.293, C=752.625, D=236.138 |
| `Nivel` | Nivel dentro del grupo (1-N) | Ej. B1, B2... |
| `Clasificacion` | Grupo + Nivel concatenado | Ej. "B3" — variable de tratamiento para la frontera B/C |

## 2. Llave de hogar en cada fuente (NO compatibles entre sí — de ahí el Hot-Deck)

| Fuente | Llave | Consecutivo |
|---|---|---|
| Sisbén IV | `cod_mpio + zona + llave + corte` (+`hogar` en Viviendas) | Local por municipio/zona — NO es DIRECTORIO |
| GEIH | `DIRECTORIO + SECUENCIA_P + HOGAR` | Nacional DANE |
| IPM | `DIRECTORIO + SECUENCIA_ENCUESTA + SECUENCIA_P` | Nacional DANE |

## 3. Variables comunes de matching (X) — vivienda

| Sisbén | GEIH | IPM | Concepto |
|---|---|---|---|
| `viv002` | `P4020` | `paredes` | Material paredes |
| `viv003` | `P4030S1` | `pisos` | Material pisos |
| `viv005` | `P8520S3` | `alcantarillado` | Alcantarillado |
| `viv008` | `P8520S5` | `acueducto` | Acueducto |
| `viv009` / `hog002` | `P5010` | — | Número de cuartos |
| `hog027` | `PERSONAS` (IPM) | `personas` | Total personas del hogar (insumo de hacinamiento) |

## 4. Variables comunes de matching (X) — demografía del jefe de hogar

| Sisbén (Personas, filtrar `PER003`="Jefe") | GEIH | Concepto |
|---|---|---|
| `PER001` | `P6020` | Sexo |
| `PER002` | `P6040` | Edad |
| `PER017` | `P8587S1` | Nivel educativo |
| `PER019` / `PER020` | `P6260` / posición ocupacional | Actividad económica |

## 5. Geografía (siempre disponible en las 3 fuentes)

`cod_mpio` (Sisbén) ↔ código de municipio/departamento equivalente en GEIH/IPM. Nivel mínimo de agregación común para el escenario de Área Pequeña si llegara a necesitarse.

## 6. ⚠️ Variables que existen pero NO se usan (circularidad confirmada)

| Variable Sisbén | Por qué se excluye |
|---|---|
| `I1`–`I15` (Personas) | Privaciones Alkire-Foster **proxy calculadas por el propio Sisbén** — mismas 15 del IPM. Usarlas como Outcome sería medir el algoritmo con su propia regla. |
| `H_5` (Personas) | "Proxy: Indicador de pobreza multidimensional" — versión interna de Sisbén del IPM. Mismo problema de circularidad. |

**Regla aplicada:** el Outcome del análisis causal se construye exclusivamente con IPM (DANE, fuente independiente) y GEIH — nunca con las columnas proxy internas de Sisbén, aunque estén disponibles en el archivo.
