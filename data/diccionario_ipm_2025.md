# Diccionario de variables — IPM 2025 (DANE)

Extraído automáticamente del DDI XML oficial
(`DANE-DIMPE-POBREZA-MULTIDIMENSIONAL-2025.xml`, IDNo
`DANE-DIMPE-POBREZA-MULTIDIMENSIONAL-2025`, prod_date 2026-04-10).

Total de variables descritas en el DDI: 146

> **Nota:** este DDI describe varias bases relacionadas (nivel hogar
> y nivel persona, base nacional y base departamental) bajo el mismo
> `<dataDscr>`, por eso hay nombres repetidos con distinta capitalización
> (p. ej. `IPM` vs `ipm`, `FEX_C` vs `fex_c`). Confirmar el nombre exacto
> de columna una vez se descargue el archivo de datos real (no solo la
> ficha DDI), y actualizar `2_limpieza.py` según corresponda.

| Variable | Etiqueta |
|---|---|
| `PERIODO` | PERIODO |
| `DIRECTORIO` | DIRECTORIO |
| `SECUENCIA_ENCUESTA` | SECUENCIA_ENCUESTA |
| `SECUENCIA_P` | SECUENCIA_P |
| `P5010` | ¿en cuántos de esos cuartos duermen las personas de este hogar? |
| `P8526` | ¿con qué tipo de servicio sanitario cuenta el hogar? |
| `P8530` | El agua para preparar los alimentos, la obtienen principalmente de: |
| `P1075` | ¿El hogar tiene conexión a internet? |
| `P1077S21` | ¿Cuáles de los siguientes bienes o servicios posee éste hogar? Computador de escritorio |
| `P1077S22` | ¿Cuáles de los siguientes bienes o servicios posee éste hogar? Computador portátil |
| `P1077S23` | ¿Cuáles de los siguientes bienes o servicios posee éste hogar? Tableta |
| `fex_c` | Factor de expansión Hogar |
| `personas` | ¿cuántas personas componen este hogar? |
| `paredes` | Privación por inadecuado material de paredes exteriores |
| `pisos` | Privación por inadecuado material de pisos |
| `alcantarillado` | Privación por inadecuada eliminación de excretas |
| `acueducto` | Privación por no acceso a fuente de agua mejorada |
| `empleo_formal` | Privación por Tasa de Empleo Formal |
| `desempleo_larga_duracion` | Privación por Desempleo de Larga Duración |
| `barreras_acceso_salud` | Privación por barreras de acceso a salud |
| `aseguramiento_salud` | Privación por no aseguramiento en salud |
| `trabajo_infantil` | Privación por Trabajo Infantil |
| `atencion_integral` | Privación por Atención Integral a la Primera Infancia |
| `inasistencia_escolar` | Privación por Inasistencia Escolar |
| `rezago_escolar` | Privación por rezago escolar |
| `anallfabetismo` | Privación por Analfabetismo |
| `logro_educativo` | Privación por Bajo Logro Educativo |
| `hacinamiento` | Privación por hacinamiento crítico |
| `ipm` | Índice de Pobreza Multidimensional |
| `pobre` | Pobre |
| `fexp` | Factor de expansión Personas |
| `DIRECTORIO` | SECUENCIA_P |
| `SECUENCIA_ENCUESTA` | Secuencia_encuesta |
| `SECUENCIA_P` | Secuencia_p |
| `ORDEN` | Orden |
| `P6020` | Sexo |
| `P6040` | ¿Cuántos años cumplidos tiene? |
| `P6051` | ¿Cuál es el parentesco de ... con el jefe o la jefa de este hogar? |
| `FEX_C` | Factor de Expansión |
| `P6090` | ¿Está afiliado, es cotizante o es beneficiario de alguna entidad de seguridad social en salud? (entidad promotora de salud -eps o administradora de régimen subsidiado -ars (a través del sisben) |
| `P5665` | En los últimos 30 días, ¿tuvo alguna enfermedad, accidente , problema odontológico o algún otro problema de salud que no haya implicado hospitalización |
| `P8563` | Para tratar ese problema de salud, ¿qué hizo principalmente _____? |
| `P51` | ¿Dónde o con quién permanece… durante la mayor parte del tiempo entre semana? |
| `P55` | ¿Recibe o toma ____ desayuno o almuerzo en el lugar donde permanece la mayor parte del tiempo entre semana? |
| `P774` | _____ paga por esta alimentación? |
| `P6160` | ¿sabe leer y escribir? |
| `P8587` | ¿____ actualmente estudia? (asiste al preescolar, escuela, colegio o universidad) |
| `P8587S1` | ¿Cuál es el nivel educativo más alto alcanzado por ... y el último año o grado aprobado en este nivel? |
| `P1088` | Grado o año aprobado |
| `P1088S1` | En qué nivel está matriculado______ y qué grado cursa? |
| `P6180` | Grado o año que cursa |
| `P6250` | ¿recibe en el plantel educativo alimentos (desayunos, medias nueves, almuerzos, etc.) en forma gratuita o por un pago simbólico? |
| `P6260` | ¿En que actividad ocupó...... la mayor parte del tiempo LA SEMANA PASADA? |
| `P6270` | Además de lo anterior, ¿.....realizó LA SEMANA PASADA alguna actividad paga por una hora o más? |
| `P6351` | Aunque.... no trabajó LA SEMANA PASADA, por una HORA O MÁS en forma remunerada, ¿tenía durante esa semana algún trabajo o negocio por el que recibe ingresos? |
| `P7250` | ¿....trabajó LA SEMANA PASADA en un negocio por UNA HORA O MÁS sin que le pagaran? |
| `P6920` | Si le hubiera resultado algún trabajo a …. ¿estaba disponible LA SEMANA PASADA para empezar a trabajar? |
| `P8586` | ¿Durante cuántas semanas ha estado o estuvo ___ buscando trabajo? |
| `P3336S1` | ¿Está ..... cotizando actualmente a un fondo de pensiones? |
| `P3336S2` | ¿En qué modalidad(es) o a través de qué medio(s) se encuentra estudiando ... actualmente? 1. Presencial |
| `P3336S3` | ¿En qué modalidad(es) o a través de qué medio(s) se encuentra estudiando ... actualmente? 2. Virtual (a través de internet en computador de escritorio, portátil, tableta o celular) |
| `P3337` | ¿En qué modalidad(es) o a través de qué medio(s) se encuentra estudiando ... actualmente? 3. Alternancia entre presencial y virtual |
| `P6240` | ¿... tuvo comunicación con sus maestros la semana pasada? |
| `P1082S2` | ¿Tiene Teléfono celular inteligente (smartphone)? |
| `P3` | Clase |
| `P4005` | Material predominante de las paredes exteriores |
| `P4015` | Material predominante de los pisos |
| `P8520S3` | Alcantarillado |
| `P8520S5` | Acueducto |
| `DIRECTORIO` | Directorio |
| `REGION` | Region |
| `DEPARTAMENTO` | Departamento |
| `PERSONAS` | ¿cuántas personas componen este hogar? |
| `FEX_C` | Factor de expansión Hogar |
| `analfabetismo` | Privación por Analfabetismo |
| `IPM` | Índice de Pobreza Multidimensional |
| `POBRE` | Pobre |
| `FEXP` | Factor de expansión Personas |
| `PERIODO` | Privación por inadecuado material de paredes exteriores |
| `P1075` | Privación por hacinamiento crítico |
| `P1077S21` | Índice de Pobreza Multidimensional |
| `P1077S22` | Pobre |
| `P1077S23` | Factor de expansión Personas |
| `Directorio` | Directorio |
| `Secuencia_encuesta` | Secuencia_encuesta |
| `Secuencia_p` | Secuencia_p |
| `Orden` | Orden |
| `P6040` | ¿cuántos años cumplidos tiene? |
| `P6051` | ¿cuál es el parentesco de ... Con el jefe o la jefa de este hogar? |
| `Fex_c` | Factor de expansión |
| `P6090` | ¿está afiliado, es cotizante o es beneficiario de alguna entidad de seguridad social en salud? (entidad promotora de salud -eps o administradora de régimen subsidiado -ars (a través del sisben) |
| `P51` | ¿dónde o con quién permanece… durante la mayor parte del tiempo entre semana? |
| `P55` | ¿recibe o toma <...> desayuno o almuerzo en el lugar donde permanece la mayor parte del tiempo entre semana? |
| `P8586` | ¿____ actualmente estudia? (asiste al preescolar, escuela, colegio o universidad) |
| `P8587` | ¿cuál es el nivel educativo más alto alcanzado por ... Y el último año o grado aprobado en este nivel? |
| `P8587s1` | Grado o año aprobado |
| `P1088` | En qué nivel está matriculado______ y qué grado cursa? |
| `P1088s1` | Grado o año que cursa |
| `P6180` | ¿recibe en el plantel educativo alimentos (desayunos, medias nueves, almuerzos, etc.) en forma gratuita o por un pago simbólico? |
| `P6240` | ¿en que actividad ocupó...... la mayor parte del tiempo la semana pasada? |
| `P6250` | Además de lo anterior, ¿.....Realizó la semana pasada alguna actividad paga por una hora o más? |
| `P6260` | Aunque.... no trabajó la semana pasada, por una hora o más en forma remunerada, ¿tenía durante esa semana algún trabajo o negocio por el que recibe ingresos? |
| `P6270` | ¿....trabajó la semana pasada en un negocio por una hora o más sin que le pagaran? |
| `P6351` | Si le hubiera resultado algún trabajo a …. ¿estaba disponible la semana pasada para empezar a trabajar? |
| `P7250` | ¿durante cuántas semanas ha estado o estuvo <...> buscando trabajo? |
| `P6920` | ¿está ..... Cotizando actualmente a un fondo de pensiones? |
| `P3336s1` | ¿en qué modalidad(es) o a través de qué medio(s) se encuentra estudiando ... Actualmente? 1. Presencial |
| `P3336s2` | ¿en qué modalidad(es) o a través de qué medio(s) se encuentra estudiando ... Actualmente? 2. Virtual (a través de internet en computador de escritorio, portátil, tableta o celular) |
| `P3336s3` | ¿en qué modalidad(es) o a través de qué medio(s) se encuentra estudiando ... Actualmente? 3. Alternancia entre presencial y virtual |
| `P3337` | ¿... Tuvo comunicación con sus maestros la semana pasada? |
| `P1082s2` | ¿tiene teléfono celular inteligente (smartphone)? |
