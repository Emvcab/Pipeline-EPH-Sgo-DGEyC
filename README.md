# Pipeline EPH — Santiago del Estero

**Versión del producto / portal:** `3.4.0` (cierre metodológico)  
**Versión interna del motor ETL:** `3.2.1` (identificador técnico conservado por compatibilidad)

Sistema para descargar, integrar, validar y calcular indicadores trimestrales a partir de microdatos públicos de la Encuesta Permanente de Hogares (EPH) del INDEC para el **Aglomerado 18 — Santiago del Estero - La Banda**.

El snapshot de referencia incluido en el repositorio cubre **13 períodos**, desde `2023T1` hasta `2026T1`. La V3.4.0 consolida la capa analítica de V3.3 y fortalece la metodología: incorpora tasas específicas de 14 años y más, corrige el ponderador del ingreso principal `P21` para usar `PONDIIO`, conserva `ADECOCUR` para deciles y documenta una validación externa reproducible contra publicaciones oficiales del INDEC.

> **Nota de publicación:** el `data_snapshot/` incluido fue generado antes del cierre metodológico V3.4.0. Su histórico agregado todavía no contiene las nuevas columnas 14+ y su metadata de ingresos conserva la fórmula anterior con `PONDERA`. Antes de publicar el tag/release final para uso del portal, el snapshot debe regenerarse con el código V3.4.0 y volver a validarse. El código y la suite metodológica sí corresponden al cierre V3.4.0.

**Entregado a:** Dirección General de Estadística y Censos (DGEyC) — Santiago del Estero
**Desarrollado por:** Práctica Profesionalizante II · ITSE 2026
**Grupo:** Achaval María José · Cabaña Emilio · Constantinidi Leandro · Gomez Cinthia · Pinto Villegas Eduardo


## Novedades de la versión 3.4.0

La V3.4.0 cierra, por el momento, la evolución metodológica del producto sobre la base estable del ETL 3.2.1 y la capa analítica incorporada en V3.3. Los principales resultados son:

- tasas específicas de **actividad, empleo y desocupación para población de 14 años y más**, calculadas con `PONDERA`;
- conservación de las tasas de 10 años y más como referencia histórica complementaria;
- ingreso promedio ponderado de la ocupación principal (`P21`) calculado con **`PONDIIO`**, sin sustitución silenciosa por `PONDERA` cuando el ponderador específico no está disponible;
- deciles de ingreso mediante **`ADECOCUR`**, sin fabricar deciles locales alternativos;
- validación empírica de las tasas principales contra publicaciones oficiales del INDEC: **27/27 concordancias**, correspondientes a 9 trimestres (`2024T1`–`2026T1`) y 3 indicadores (actividad, empleo y desocupación);
- bloque **Validación metodológica contra INDEC** en la pestaña Calidad y auditoría del portal, con evidencia descargable y matriz metodológica;
- recuperación y prueba de la exportación del **reporte PDF institucional**;
- suite automatizada consolidada en **97 tests aprobados**.

El portal conserva además lo incorporado en V3.3: Plotly, filtros temporales, comparación entre períodos, brechas y perfiles por sexo, edad y nivel educativo, deciles de ingreso e interpretación descriptiva. Las diferencias entre grupos o períodos no se presentan como causalidad ni como significancia estadística.

**Decisión de alcance:** la comparación territorial Santiago del Estero–La Banda vs. NOA vs. total EPH no forma parte del cierre V3.4.0. Tras la revisión con el equipo EPH se decidió no incorporarla en esta etapa. El alcance territorial permanece centrado en el **Aglomerado 18**.

## Alcance

El proyecto automatiza las tareas necesarias para descargar, integrar, validar y calcular indicadores trimestrales a partir de microdatos públicos. Usa `PONDERA` para tasas, expansiones generales e informalidad y `PONDIIO` para el promedio ponderado de `P21`; conserva valores faltantes, produce metadatos y bloquea resultados que no superan los controles críticos.

El Hito 3 se presenta mediante un dashboard institucional para usuarios no técnicos. Machine Learning podrá evaluarse en una etapa posterior, una vez definido un problema institucional concreto, con datos suficientes y validación metodológica.

El Aglomerado 18 representa conjuntamente Santiago del Estero y La Banda. Los microdatos públicos no permiten separar ambas ciudades ni evaluar encuestadores o personal de carga.

## Indicadores

Indicadores principales:

- `tasa_actividad_oficial` = PEA expandida / población total expandida × 100.
- `tasa_empleo_oficial` = ocupados expandidos / población total expandida × 100.
- `tasa_desocupacion` = desocupados expandidos / PEA expandida × 100.
- `proporcion_inactiva_total` = 100 - tasa de actividad oficial. Es complementaria.

Indicadores específicos de población de 14 años y más:

- `tasa_actividad_14_mas`.
- `tasa_empleo_14_mas`.
- `tasa_desocupacion_14_mas`.

Se calculan con `PONDERA` y constituyen la referencia específica vigente para el análisis por edad mínima de 14 años.

Indicadores específicos de población de 10 años y más:

- `tasa_actividad_10_mas`.
- `tasa_empleo_10_mas`.
- `tasa_inactividad_10_mas`.

Se conservan como referencia histórica complementaria y no sustituyen las tasas específicas 14+.

Los nombres anteriores `tasa_actividad`, `tasa_empleo` y `tasa_inactividad` correspondían al denominador de 10 años y más. La migración los renombra explícitamente y no cambia su significado en silencio.

El ingreso promedio ponderado de la ocupación principal (`P21`) usa `PONDIIO`; no se reemplaza por `PONDERA` si ese ponderador específico no está disponible. Los deciles usan `ADECOCUR` cuando la variable existe. Los ingresos son nominales y no representan directamente variaciones del poder adquisitivo; requieren deflactación para comparaciones reales. En `2023T1`, `2023T2` y `2023T3`, la variable necesaria para estimar informalidad no está disponible. Por ese motivo, el indicador se presenta como no disponible y no se realiza imputación ni se reemplazan faltantes por cero.

## Estructura

```text
Pipeline-EPH-Sgo-DGEyC/
├── src/pipeline.py                 Pipeline, validaciones y publicación segura
├── src/monitor_actualizaciones.py  Monitor y prevalidación de nuevas publicaciones
├── src/portal_admin.py             Lógica auxiliar del portal administrativo
├── src/visualizacion.py            Rangos, filtros temporales y comparaciones del portal
├── src/reporte_pdf.py              Generación del reporte PDF institucional
├── src/validacion_metodologica.py   Utilidades de contraste metodológico
├── portal/app.py                   Portal Streamlit (consulta + administración)
├── scripts/eda_eph_sde.py         Script EDA para ejecución local/VS Code
├── scripts/validar_contra_indec.py  Regeneración del contraste metodológico
├── notebooks/EDA_EPH_SDE.ipynb    Notebook EDA demostrativo (Jupyter; Colab sólo como demo)
├── tests/test_pipeline.py          Suite automatizada del ETL
├── tests/test_monitor_actualizaciones.py  Pruebas del monitor
├── tests/test_visualizacion.py     Pruebas de rangos y filtros temporales
├── data/                           ZIP y TXT locales, excluidos de Git
├── results/                        Salidas locales, excluidas de Git
├── data_snapshot/                  Agregados validados para Streamlit Cloud
├── logs/                           Registro operativo local
└── docs/
    ├── DICCIONARIO_DATOS.md
    ├── METODOLOGIA.md
    ├── MATRIZ_VALIDACION_METODOLOGICA.md
    ├── GUIA_USO.md
    ├── MONITOR_ACTUALIZACIONES.md
    ├── PORTAL_ADMINISTRACION.md
    └── ARQUITECTURA.md
```

`data_snapshot/` contiene sólo histórico e indicadores agregados, control de calidad agregado, estados, validaciones, metadatos, manifiesto y documentación. No contiene ZIP, microdatos individuales ni bases unidas.

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux o macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Entorno de ejecución y rol del notebook

El **entorno operativo del proyecto es Python local**: el ETL, el monitor, los scripts auxiliares, los tests y Streamlit se ejecutan desde una terminal ubicada en la raíz del repositorio. Las dependencias se administran mediante `requirements.txt`; el código no ejecuta `pip install` internamente. Esta separación hace que el entorno sea reproducible y evita que un bloque de análisis modifique la instalación mientras se ejecuta.

`notebooks/EDA_EPH_SDE.ipynb` es un recurso **demostrativo y exploratorio** construido sobre el histórico agregado ya generado por el pipeline. Puede abrirse en Jupyter y, si se desea, mostrarse en Colab, pero Colab no es el mecanismo de ejecución del sistema ni reemplaza al ETL. El notebook no descarga microdatos, no instala dependencias y no publica resultados.

## Ejecución

```bash
# Un trimestre
python src/pipeline.py --anio 2025 --trimestre 4

# Un año
python src/pipeline.py --anio 2025

# Todos los períodos configurados
# Desde 3.2.1, omite automáticamente períodos futuros que nunca fueron procesados.
python src/pipeline.py --todos

# Calendario local y fechas esperadas
# No consulta INDEC en línea; para disponibilidad real usar el monitor.
python src/pipeline.py --calendario

# Volver a descargar un ZIP
python src/pipeline.py --anio 2025 --trimestre 4 --forzar
```

Para actualizar localmente el snapshot sólo después de una validación exitosa:

```bash
python src/pipeline.py --publicar-snapshot
```

Este comando no despliega la aplicación en Streamlit Cloud. Sólo prepara los archivos agregados que deben revisarse antes de versionarlos.

### Cómo interpretar `--calendario` (v3.2.1)

El calendario es un **control local**, no un verificador web. Combina la fecha esperada de publicación con `results/estado_periodos.csv`:

- `VALIDADO` / `PUBLICADO` / otros estados registrados: resultado real de una corrida local del pipeline.
- `SIN PROCESAR`: la fecha esperada ya fue alcanzada, pero no existe un estado local para ese período. Antes de procesarlo se debe consultar el monitor.
- `FUTURO`: todavía no corresponde esperar ese trimestre según el calendario configurado.

Para saber si el ZIP de microdatos está efectivamente disponible en INDEC se usa `python src/monitor_actualizaciones.py`. Esta separación evita confundir **fecha esperada**, **disponibilidad real en INDEC** y **estado del histórico local**.

## Monitor de actualizaciones INDEC

La versión 3.1 incorpora un **módulo de actualización asistida** que consulta si existen nuevos trimestres publicados por INDEC sin modificar automáticamente el histórico ni el snapshot. La revisión humana continúa siendo obligatoria.

```bash
# Consultar si hay nuevas publicaciones esperables
python src/monitor_actualizaciones.py

# Detectar y prevalidar el primer trimestre nuevo disponible
python src/monitor_actualizaciones.py --prevalidar

# Prevalidar de forma explícita un período
python src/monitor_actualizaciones.py --anio 2026 --trimestre 1 --prevalidar
```

La prevalidación descarga el ZIP oficial, verifica estructura, filtra el Aglomerado 18, calcula indicadores y aplica los controles críticos del pipeline en un área de auditoría separada (`results/monitor_actualizaciones/`). También compara el nuevo trimestre con el último histórico y genera alertas orientativas ante variaciones amplias de tasas, tamaño muestral o población expandida. **Estas alertas no son pruebas de significancia estadística y nunca publican ni invalidan por sí solas un período.**

Si la revisión es satisfactoria, la incorporación sigue utilizando el flujo normal y explícito:

```bash
python src/pipeline.py --anio 2026 --trimestre 1
python src/pipeline.py --publicar-snapshot
```

El repositorio incluye además un workflow semanal de GitHub Actions (`.github/workflows/monitor-eph.yml`) que ejecuta únicamente la consulta de disponibilidad y guarda el reporte como artefacto. No ejecuta la publicación.

## Salidas, metadatos y manifiesto

Cada CSV exportado queda acompañado por `nombre_archivo.meta.json`.

| Salida | Clasificación |
|---|---|
| `historico_SDE.csv` | Crítica |
| `indicadores_SDE_<periodo>.csv` | Analítica |
| `calidad_datos_SDE_<periodo>.csv` | Calidad |
| `validacion_esquema_<periodo>.json` | Auditoría |
| `validacion_publicacion_<periodo>.json` | Auditoría |
| `estado_periodos.csv` | Auditoría |
| logs | Operativa |
| gráficos | Visualización |
| `manifest_salidas.json` y snapshot | Disponibilización |

Los metadatos documentan fuente, período, estructura, variables, tipos, unidades, fórmulas, filtros, nulos, códigos especiales, ponderador, advertencias, estado de validación, hash e identificador de ejecución. `results/manifest_salidas.json` relaciona cada salida con su metadata.

## Control previo a publicación

Estados posibles: `PENDIENTE`, `DESCARGADO`, `PROCESADO`, `EN_REVISION`, `VALIDADO`, `FALLIDO` y `PUBLICADO`.

Antes de promover un período se comprueban descarga y ZIP, archivos individual y hogar, esquema obligatorio, Aglomerado 18, población total positiva, duplicados, rango de tasas, complementariedad actividad-inactividad, desocupación calculable, filas razonables, archivos y metadatos, y disponibilidad de informalidad.

Las salidas se construyen en una carpeta temporal. Ante una falla crítica, el período queda `FALLIDO`, se registra un mensaje entendible y no se reemplaza el histórico ni el snapshot vigente.

## Portal web

Ejecución exacta desde la raíz:

```bash
python -m streamlit run portal/app.py
```

La V3.4.0 consolida un portal de **ocho secciones**: resumen ejecutivo, evolución laboral, brechas y perfiles, ingresos, calendario, calidad y auditoría, documentación y descargas, y administración. Las vistas de consulta usan `results/` únicamente si el último período es `VALIDADO` o `PUBLICADO`; en caso contrario conservan el último `data_snapshot/` validado. Calidad y auditoría incluye el bloque de validación metodológica contra INDEC y acceso a la evidencia 27/27.

El área administrativa permite consultar INDEC, prevalidar una nueva publicación y revisar alertas sin usar la terminal. La incorporación final está bloqueada por defecto y requiere clave administrativa, `admin_enable_writes=true`, un reporte `LISTO_PARA_REVISION`, confirmación humana y la validación transaccional final del pipeline. Ver `docs/PORTAL_ADMINISTRACION.md`.

Para nuevos despliegues de Streamlit Cloud, configurar como archivo principal:

```text
portal/app.py
```

La aplicación Streamlit vive únicamente en `portal/app.py`. La carpeta `notebooks/` queda reservada exclusivamente para archivos Jupyter (`.ipynb`); los scripts Python auxiliares viven en `scripts/`.

En despliegues con almacenamiento efímero se recomienda mantener la publicación final deshabilitada y ejecutarla en infraestructura persistente de la Dirección.

## Tests

```bash
python -m pytest tests -q
```

Las pruebas escriben sólo en directorios temporales y verifican fórmulas, migración de nombres, rangos, metadatos, manifiesto, bloqueo de publicación, conservación del snapshot, carga agregada y rutas relativas.

Resultado de cierre de la V3.4.0: **97 tests aprobados**. Además, la validación metodológica reproduce **27 de 27** valores publicados por INDEC para actividad, empleo y desocupación en 9 trimestres (`2024T1`–`2026T1`). La validación manual histórica de 3.2.1 se conserva en `docs/VALIDACION_LOCAL_V3_2_1.md` como evidencia de esa etapa.

## Devolución institucional y mejoras incorporadas

- Portal web adaptado a usuarios no técnicos, con consulta y administración separadas.
- Calendario visible en web, con distinción explícita entre estado local y disponibilidad real verificada por el monitor.
- Metadatos automáticos para cada salida tabular.
- Clasificación de cargas y manifiesto general.
- Control previo a publicación y estados por período.
- Calendario, contingencia y conservación del último resultado validado.
- Snapshot agregado para ejecución independiente del ETL.
- Arquitectura ampliable mediante funciones documentadas y salidas trazables.
- Validación metodológica externa reproducible contra INDEC, con matriz y evidencia descargable.
- Tasas específicas 14+ y ponderación de `P21` mediante `PONDIIO`.

## Documentos históricos

`docs/INFORME_FINAL_HITO3.md`, `docs/RESUMEN_ENTREGA_ENTIDAD.md` y el reporte ejecutivo 4T2025 se conservan como evidencia de los hitos en la fecha en que fueron entregados. Sus cifras de períodos/tests no se reescriben retroactivamente; la situación vigente se resume en este README, el CHANGELOG y `docs/VALIDACION_LOCAL_V3_2_1.md`.

## Limitaciones y reporte anterior

- Los indicadores se calculan a partir de microdatos públicos y no sustituyen procedimientos institucionales confirmados.
- Los indicadores operativos de campo requieren bases internas y definiciones institucionales.
- El archivo `docs/Reporte_Ejecutivo_EPH_SDE_4T2025.pdf` se conserva como antecedente, pero no se ofrece en el dashboard: utiliza los nombres y denominadores anteriores y contiene una línea futura que ya no representa el alcance del Hito 3. No existe una fuente editable equivalente en el repositorio.

## Cierre de V3.4.0

La V3.4.0 se considera **cerrada por el momento** como versión metodológica estable del repositorio actual. El alcance conserva el Aglomerado 18 y no incorpora comparación territorial NOA/nacional. Quedan como líneas futuras, sujetas a priorización institucional: tratamiento inferencial asociado al diseño muestral, contraste externo de informalidad, revisión del control interno basado en `REALIZADA` y mejoras de escalabilidad/arquitectura.

Las notas preparadas para el release se encuentran en `docs/RELEASE_NOTES_V3_4_0.md`.

## Fuente

Encuesta Permanente de Hogares — Instituto Nacional de Estadística y Censos (INDEC), República Argentina: <https://www.indec.gob.ar>.


## Análisis segmentado V3.3

La V3.3 agrega una capa analítica sobre el ETL 3.2.1 para explorar brechas por sexo, edad y nivel educativo, además de ingresos por deciles cuando `ADECOCUR` y el ponderador específico `PONDIIO` están disponibles. El portal muestra estas salidas en **Brechas y perfiles**. Son estimaciones descriptivas de la EPH y deben leerse junto con las consideraciones de error muestral.
