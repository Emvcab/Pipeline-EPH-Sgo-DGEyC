# Pipeline EPH — V3.4.0

## Cierre metodológico

La V3.4.0 consolida la evolución metodológica del Pipeline EPH para el **Aglomerado 18 — Santiago del Estero–La Banda**. Esta versión se considera cerrada por el momento y mantiene el alcance territorial centrado en el aglomerado.

### Principales mejoras

- Tasas específicas de actividad, empleo y desocupación para población de **14 años y más**.
- Tasas laborales e informalidad con `PONDERA`.
- Ingreso ponderado de la ocupación principal `P21` con **`PONDIIO`**, sin fallback silencioso a `PONDERA`.
- Deciles mediante **`ADECOCUR`** cuando está disponible.
- Validación contra publicaciones oficiales del INDEC: **27/27 concordancias** en 9 trimestres (`2024T1`–`2026T1`) para actividad, empleo y desocupación.
- Matriz de validación metodológica y evidencia CSV descargables desde el portal.
- Bloque de validación metodológica visible en **Calidad y auditoría**.
- Reporte PDF institucional recuperado e integrado.
- **97 tests aprobados**.

### Alcance

La comparación territorial Santiago del Estero–La Banda vs. NOA vs. total EPH no se incorpora en este release. Tras la revisión con el equipo EPH se definió que no es necesaria para esta etapa.

Las diferencias entre períodos y grupos continúan siendo descriptivas. Esta versión no implementa errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral. El contraste externo de informalidad y la revisión del control interno de no respuesta de hogares mediante `REALIZADA` quedan como pendientes metodológicos documentados.

### Control previo al release

El código V3.4.0 y sus 97 tests están cerrados. Sin embargo, el `data_snapshot/` incluido en la copia revisada fue generado antes del ajuste metodológico final: no contiene las columnas 14+ en el histórico y su metadata de ingreso ponderado todavía registra `PONDERA`. Para publicar el release como versión final del portal, debe regenerarse el snapshot con el código V3.4.0 y repetirse la suite.

### Trazabilidad

- Snapshot: **13 períodos**, `2023T1`–`2026T1`.
- Evidencia metodológica: `docs/validacion_metodologica_indec.csv`.
- Matriz: `docs/MATRIZ_VALIDACION_METODOLOGICA.md`.
- Suite: `python -m pytest tests -q` → **97 passed**.

**Tag recomendado:** `v3.4.0`  
**Título del release:** `V3.4.0 — Cierre metodológico y validación contra INDEC`


### Coherencia del entorno de ejecución

Como parte del cierre se revisó la separación entre entorno operativo y material demostrativo: el sistema se ejecuta con Python local y dependencias administradas por `requirements.txt`; el EDA no instala paquetes durante su ejecución y el notebook queda documentado como apoyo exploratorio/demostrativo. Esta corrección responde a la devolución docente sobre la necesidad de que cada bloque refleje el entorno real en el que se usa el proyecto.
