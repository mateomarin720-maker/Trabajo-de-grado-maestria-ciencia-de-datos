# Carpeta: Datos y Conexiones
---
Esta carpeta almacena todos los activos de datos del proyecto, organizados
por su estado en el ciclo de vida. Por la naturaleza sensible de los
microdatos del Sisbén IV y la GEIH, **el contenido de las subcarpetas no
se versiona** (ver `.gitignore`); solo se versionan estos `README.md` y
[`catalogo.yaml`](catalogo.yaml).

## Catálogo de fuentes

El detalle de cada fuente (portal, tipo de acceso, identificador, período
y estado de obtención) está documentado en
[`catalogo.yaml`](catalogo.yaml). Resumen:

| Fuente | Entidad | Tipo de acceso | Estado |
|---|---|---|---|
| GEIH | DANE | Microdatos anonimizados (registro) | 🔧 Por gestionar |
| Sisbén IV | DNP | Solicitud institucional | ⏳ Por solicitar |
| DPS (Familias en Acción, Ingreso Solidario) | DPS | Solicitud institucional / convenio | ⏳ Por solicitar |
| IPM | DANE | Indicadores agregados abiertos + microdatos GEIH | 🔧 Por gestionar |
| RUI (Registro Único de Víctimas) | UARIV | Solicitud institucional | ⏳ Por solicitar |

## Subcarpetas y artefactos correspondientes

### `0_raw/`
- **Propósito**: Almacenar los datos originales sin modificación alguna.
- **Regla de oro**: Esta carpeta es de **solo lectura**. Toda transformación
  debe partir de una copia en `1_processed/`.

### `1_processed/`
- **Propósito**: Datos limpios, armonizados y preparados para el análisis
  causal.
- **Artefactos esperados**:
  - Tabla unificada a nivel hogar con: tratamiento (puntaje/grupo Sisbén
    IV), outcomes de bienestar, confusores observables y pobreza latente.
  - Versiones codificadas y escaladas listas para DML / Causal Forest.

### `2_models/`
- **Propósito**: Guardar objetos serializados de estimadores y resultados
  intermedios.
- **Artefactos esperados**:
  - Modelos LASSO/Ridge y SHAP (OE1).
  - Modelos de suficiencia explicativa (OE2).
  - Objetos DML / Causal Forest con su identificación documentada (OE3).

---
### ⚠️ Nota de seguridad importante

**NUNCA** subas microdatos del Sisbén, GEIH, DPS o RUI con información
personal a repositorios de Git. El `.gitignore` ya bloquea el contenido
de estas carpetas; no lo modifiques sin coordinación con el equipo y el
profesor tutor.

El manejo de los datos debe ceñirse a la **Ley 1581 de 2012** (protección
de datos personales) y a los términos de uso que establezca el DNP/DANE/DPS/UARIV.
