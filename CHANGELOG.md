# Historial de cambios

## 3.4.0 — 2026-10-14

### Cierre metodológico
- Se incorporan tasas específicas de actividad, empleo y desocupación para población de **14 años y más**, usando `PONDERA`.
- Las tasas de 10 años y más se conservan como referencia histórica complementaria.
- El promedio ponderado de `P21` usa `PONDIIO`; se elimina el uso de `PONDERA` como sustituto silencioso cuando falta el ponderador específico.
- Los deciles utilizan `ADECOCUR` cuando está disponible; no se construyen deciles locales alternativos.
- Se incorpora `docs/MATRIZ_VALIDACION_METODOLOGICA.md` y evidencia reproducible en `docs/validacion_metodologica_indec.csv`.
- Se contrastan actividad, empleo y desocupación contra publicaciones oficiales del INDEC para 9 trimestres (`2024T1`–`2026T1`): **27/27 comparaciones concordantes** al nivel de redondeo publicado.
- La pestaña **Calidad y auditoría** muestra el bloque de validación metodológica, su estado y las descargas asociadas.
- La exportación PDF institucional queda recuperada e integrada al portal.
- Suite de cierre: **97 tests aprobados**.

### Alcance de la versión
- La comparación territorial Santiago del Estero–La Banda vs. NOA vs. total EPH **no se incorpora** en V3.4.0. Tras la revisión con el equipo EPH se definió que no es necesaria para esta etapa.
- El análisis continúa centrado en el **Aglomerado 18 — Santiago del Estero–La Banda**.
- Las comparaciones entre períodos y grupos siguen siendo descriptivas: esta versión no calcula errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral.
- La informalidad continúa con contraste externo pendiente. El control interno `tasa_no_respuesta_hogar` basado en `REALIZADA` queda documentado como punto técnico a revisar antes de interpretarlo como indicador de no respuesta.

### Ajuste de coherencia técnica tras devolución docente
- Se explicita que el entorno operativo del proyecto es **Python local**, ejecutado desde la raíz del repositorio.
- Se elimina del EDA la instalación automática de librerías en tiempo de ejecución: las dependencias se preparan mediante `requirements.txt`.
- El notebook queda identificado como recurso demostrativo/exploratorio. Colab puede utilizarse para una demostración, pero no es el entorno de ejecución del ETL, el monitor ni Streamlit.
- La documentación histórica deja de limitarse a frases genéricas y explica **cómo**, **por qué** y **para qué** se introdujeron las principales decisiones de arquitectura y refactorización.

### Documentación y release
- README, metodología, arquitectura, diccionario, guía de uso, manual técnico, manual de usuario, matriz metodológica y roadmap se actualizan al estado de cierre V3.4.0.
- Se agrega `docs/RELEASE_NOTES_V3_4_0.md` como texto base del release de GitHub.
- `PORTAL_VERSION` pasa de `3.4.0-dev` a `3.4.0`; el identificador interno `PIPELINE_VERSION = 3.2.1` se conserva por compatibilidad.

### Agregado — reporte PDF institucional por período
- El Resumen ejecutivo permite descargar un PDF estático del período seleccionado.
- El reporte incluye indicadores principales, comparación temporal, evolución reciente, ingresos nominales, brechas y perfiles cuando la salida segmentada está disponible, lecturas descriptivas y notas metodológicas.
- El PDF se genera exclusivamente desde salidas agregadas validadas; no recalcula fórmulas ni accede a microdatos.
- Si falta la salida segmentada, el reporte sigue disponible y lo informa sin fabricar desagregaciones.
- Se incorpora `src/reporte_pdf.py`, `reportlab` como dependencia y pruebas automatizadas específicas de exportación.

### Mejorado — interpretación descriptiva de brechas
- La sección **Brechas y perfiles** incorpora una lectura automática y estrictamente descriptiva del período seleccionado.
- Para sexo, edad y educación identifica categorías con valores máximos y mínimos del indicador elegido y expresa la diferencia en puntos porcentuales.
- Para deciles dimensiona la distancia nominal entre extremos y aclara que la progresión es esperable por construcción de ADECOCUR.
- Las lecturas no infieren causalidad ni significancia estadística y muestran el rango de tamaños muestrales disponible.

### Mantenimiento de estructura del repositorio
- El portal Streamlit se ubica en `portal/app.py`; se elimina la antigua ubicación `notebooks/app.py`.
- `notebooks/` queda reservado para notebooks Jupyter de demostración/análisis (`.ipynb`); Colab puede usarse como soporte demostrativo, no como runtime del sistema.
- El script EDA local se mueve de `notebooks/eda_eph_sde.py` a `scripts/eda_eph_sde.py`.
- Los despliegues existentes deben configurar `portal/app.py` como archivo principal.
- No cambia el ETL, los indicadores, las validaciones ni la lógica administrativa.

## 3.3.0 — 2026-10-07

### Corrección metodológica previa al reprocesamiento segmentado
- Los promedios de `P21` de la nueva capa segmentada usan `PONDIIO`, el ponderador específico de ingreso de la ocupación principal publicado por INDEC.
- La expansión de la dimensión `Decil de ingreso` también usa `PONDIIO`.
- `PONDERA` se conserva para tasas laborales, informalidad y población general.
- Si `PONDIIO` no está disponible, no se fabrican promedios ni deciles alternativos.

### Profundidad analítica — respuesta a devolución DPE
- Se agrega `src/analisis_segmentado.py` para calcular brechas por sexo, edad y nivel educativo.
- Las tasas específicas por sexo usan población de 14 años y más, siguiendo la presentación de INDEC.
- Se incorporan deciles de ingreso de la ocupación principal mediante `ADECOCUR` cuando está disponible.
- El portal suma la sección **Brechas y perfiles** y mantiene advertencias sobre error muestral y alcance descriptivo.
- Las salidas segmentadas son agregadas y pueden incorporarse al snapshot; los microdatos siguen fuera del snapshot.

### Mejorado — visualización e interactividad temporal

- El portal incorpora **Plotly** para los gráficos de evolución laboral e ingresos.
- Los ejes verticales se ajustan al rango de los datos visibles en lugar de forzarse a cero cuando eso reduciría la legibilidad de las variaciones.
- El Resumen ejecutivo permite elegir un **período de referencia** y un **período de comparación**.
- Las métricas muestran diferencias descriptivas en puntos porcentuales entre los dos períodos elegidos.
- Evolución laboral e Ingresos incorporan filtros temporales `Desde` / `Hasta`.
- Se agrega `src/visualizacion.py` para aislar filtros y rangos de visualización de la lógica estadística del ETL.
- Se agregan 6 pruebas nuevas; suite total: **74 tests aprobados**.
- El motor ETL permanece en `3.2.1`; no se cambian fórmulas, validaciones críticas ni publicación transaccional.
- Esta versión inicia la respuesta técnica a la devolución de la DPE; análisis por sexo, edad, educación, deciles, contexto territorial y exportación PDF quedan planificados como siguientes incrementos.

---

## 3.2.1 — 2026-09-24

### Corregido — calendario y ejecución por lote

- Se incorpora `estado_registrado()` para distinguir un estado realmente persistido en `estado_periodos.csv` de una estimación basada únicamente en la fecha esperada.
- `--calendario` aclara que **no consulta INDEC en línea** y diferencia estados locales, `SIN PROCESAR` y `FUTURO`.
- `SIN PROCESAR` ya no implica que el ZIP esté publicado: indica que la fecha esperada fue alcanzada y remite al monitor para verificar disponibilidad real.
- `procesar_lote()` omite períodos futuros que nunca fueron registrados, evitando intentos innecesarios de descarga con `--anio` o `--todos`.
- Se conserva el monitor como única comprobación remota de disponibilidad del ZIP de microdatos.
- Se actualizan README, guías, manual técnico, arquitectura, portal y registro HTML para reflejar esta separación conceptual.
- Se agrega `docs/VALIDACION_LOCAL_V3_2_1.md` con la prueba manual realizada en VS Code.
- 3 pruebas nuevas específicas del ajuste; suite total: **68 tests**.
- `PIPELINE_VERSION` pasa a `3.2.1`.

---

## 3.2.0 — 2026-09-22

### Portal para usuarios no técnicos

- El dashboard pasa a ser un portal de siete secciones, incorporando **Calendario** y **Administración**.
- El calendario web reutiliza `fecha_publicacion_esperada()` y `estado_trimestre()`; no duplica reglas del pipeline.
- Nueva capa `src/portal_admin.py` para listar prevalidaciones y ejecutar una incorporación asistida con confirmación explícita.
- Área administrativa protegida por clave configurable fuera del repositorio.
- Publicación desde la UI deshabilitada por defecto; requiere `admin_enable_writes=true` / `EPH_ADMIN_ENABLE_WRITES=1`.
- El operador puede consultar INDEC, prevalidar, revisar controles y alertas, y luego incorporar el período sin usar la terminal.
- La publicación final vuelve a ejecutar el pipeline completo y conserva sus controles transaccionales y rollback.
- Nueva guía `docs/PORTAL_ADMINISTRACION.md` y plantilla `.streamlit/secrets.toml.example`.
- 6 pruebas nuevas del portal; suite total: **65 tests**.
- `PIPELINE_VERSION` pasa a `3.2.0`.

Todos los cambios relevantes del proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el versionado [Semantic Versioning](https://semver.org/lang/es/).


## 3.1.0 — 2026-09-22

### Agregado
- **Monitor de nuevas publicaciones EPH** (`src/monitor_actualizaciones.py`) que consulta los ZIP oficiales esperables según el calendario del pipeline.
- **Prevalidación asistida** de un trimestre nuevo sin modificar el histórico ni el snapshot vigentes.
- Comparación automática con el período anterior y alertas orientativas por variaciones amplias de tasas, tamaño muestral y población expandida.
- Reportes JSON y Markdown de prevalidación con metadatos y manifiesto de auditoría.
- Workflow semanal y ejecución manual mediante GitHub Actions para consultar novedades sin publicar datos.
- 9 pruebas automatizadas del monitor; suite total: **59 tests**.

### Cambiado
- `PIPELINE_VERSION` pasa a `3.1.0`.
- `ANIOS` incorpora 2026 para permitir el procesamiento explícito de los nuevos trimestres.

### Seguridad operativa
- El monitor **no publica automáticamente**. La promoción al histórico y al snapshot continúa requiriendo ejecución y revisión humana explícitas.
- Los umbrales de alerta se documentan como controles operativos, no como pruebas de significancia estadística.

---

## 3.0.0 — 2026-07-13

- Separación entre tasas principales sobre población total y tasas específicas de 10 años y más.
- Migración explícita de nombres históricos sin cambio silencioso de denominador.
- Metadatos completos, manifiesto general y clasificación de cargas.
- Estados por período, controles críticos y promoción transaccional.
- Snapshot agregado para Streamlit, con conservación del anterior ante fallas.
- Dashboard institucional en cinco secciones, sin afirmaciones predictivas.
- Documentación metodológica y pruebas ampliadas.

---

## [2.2.0] — 2026-06-30

### Agregado
- **Calendario de publicaciones INDEC** — flag `--calendario` muestra cronograma esperado vs estado local (procesado / esperando / futuro); la disponibilidad web se verifica por separado desde v3.1
- **Validación automática de esquema** — el pipeline verifica que las columnas esperadas estén presentes antes de procesar. Si el INDEC cambia algo crítico, el pipeline avisa antes de generar resultados
- Archivo `validacion_esquema_<periodo>.json` por trimestre con resultado de la validación
- Constantes `ESQUEMA_OBLIGATORIO_INDIVIDUAL`, `ESQUEMA_OBLIGATORIO_HOGAR`, `ESQUEMA_OPCIONAL_INDIVIDUAL`
- 7 tests nuevos (total: 31 tests pasando)

### Motivación
Implementación de sugerencia recibida en devolución institucional de la DGEyC:
> "Debería incluirse un calendario, ya que el pipeline se activa con cada nueva
> publicación y debería considerarse la contingencia, auditoría y disponibilización
> del nuevo reporte, o fallas en la extracción."

---
---

## [2.1.0] — 2026-06-30

### Agregado
- **Sistema de metadatos automáticos** — cada archivo CSV generado por el pipeline ahora se acompaña de un archivo `.meta.json` con información completa para su uso (versión del pipeline, fecha de generación, fuente, esquema de columnas con tipos y descripciones, hash de integridad SHA-256)
- Función `generar_metadatos()` con diccionario embebido de las ~30 columnas del histórico
- Función `calcular_hash()` para verificación de integridad
- Constante `PIPELINE_VERSION` para trazabilidad de versiones
- 7 tests nuevos para el sistema de metadatos (total: 24 tests)

### Cambiado
- `guardar_trimestre()` ahora genera 4 CSV + 4 JSON por trimestre procesado
- Docstring del pipeline actualizado con la nueva estructura de salidas

### Motivación
Implementación de sugerencia recibida en devolución institucional de la DGEyC:
> "Los csv o xlsx que se exporten del pipeline o las Loads deben estar acompañadas
> de metadatos para ser usables."

---


## [2.0.0] — 2026-06-26

### Cambiado
- **Refactorización estructural del pipeline**: se separaron responsabilidades, se eliminaron diagnósticos y salidas de uso único, se centralizó configuración y se reutilizó lógica repetida. Como consecuencia, el archivo principal pasó de 1.434 a 411 líneas (-71%) sin perder el flujo ETL necesario; la reducción de tamaño fue un resultado de simplificar responsabilidades, no un objetivo aislado.
- Adopción de estándares profesionales: `type hints` completos, `docstrings`, logging estructurado, manejo explícito de errores
- Centralización de constantes en sección de configuración al inicio del archivo
- Reemplazo de `os.path` por `pathlib.Path` para manejo de rutas
- Reorganización del proyecto en estructura de carpetas profesional (`src/`, `docs/`, `tests/`, `data/`, `results/`, `logs/`)

### Agregado
- `README.md` con instrucciones de instalación y uso
- `requirements.txt` con dependencias pinned
- `.gitignore` profesional
- `CHANGELOG.md` (este archivo)
- `LICENSE`
- Suite de tests básicos en `tests/`
- Documentación de arquitectura en `docs/ARQUITECTURA.md`

### Motivación de la refactorización
La implementación inicial concentraba descarga, lectura, validación, cálculo, diagnósticos y generación de salidas en un archivo amplio, lo que hacía más difícil localizar responsabilidades y probar cambios sin afectar otras etapas. La refactorización buscó **mantenibilidad, trazabilidad y capacidad de prueba**: separar qué hace cada bloque, reducir duplicación y dejar las operaciones habituales parametrizadas. Por eso un código más corto es mejor en esta versión sólo en la medida en que conserva el comportamiento necesario con menos lógica repetida y límites más claros entre responsabilidades.

### Eliminado
- Funciones de diagnóstico geográfico (información movida a documentación)
- Inventario de columnas por trimestre (uso único, no aporta valor continuo)
- Variables descriptivas decodificadas innecesarias para cálculos
- Múltiples archivos redundantes de salida
- Prints duplicados con logs

---

## [1.5.0] — 2026-06-07

### Agregado
- Lectura robusta probando 4 combinaciones de separador/codificación para tolerar variaciones reales de los TXT publicados y fallar de forma controlada si ninguna combinación resulta válida.
- Cálculo de ingreso promedio ponderado para pasar de un resumen puramente muestral a una estimación que respeta el ponderador disponible en esa etapa del proyecto.
- Reporte de calidad de datos por trimestre para dejar evidencia de nulos y códigos especiales antes de interpretar los indicadores.
- Base unida individuo-hogar por `CODUSU + NRO_HOGAR`
- Tasa de inactividad
- Sistema de logs con timestamp en carpeta `logs/`
- Flag `--forzar` para re-descargar ZIPs existentes

### Cambiado
- Migración a `pathlib.Path` en lugar de strings para rutas
- Logging básico reemplaza algunos prints

---

## [1.0.0] — 2026-05-18

### Agregado
- Versión inicial del pipeline (Hito 1): se implementó un flujo ETL ejecutable por período que construía la ruta oficial del trimestre, descargaba el ZIP de microdatos del INDEC, localizaba los archivos de personas y hogares y procesaba el contenido con Python.
- La descarga automatizada evitó bajar y organizar manualmente cada trimestre y permitió que año/trimestre fueran parámetros reproducibles de ejecución.
- Después de leer los microdatos nacionales, el proceso filtraba `AGLOMERADO == 18` para conservar exclusivamente Santiago del Estero — La Banda antes de calcular y acumular los resultados locales.
- Cálculo de tasas: actividad, empleo, desocupación, informalidad
- Cálculo de ingreso promedio simple y mediana
- Tres modos de ejecución: trimestre, año completo, todos los trimestres
- Histórico acumulado en `historico_SDE.csv`
