# Guía de uso

**Versión de referencia:** V3.5.0

## Procesar

Desde la raíz del repositorio:

```bash
python src/pipeline.py --anio 2025 --trimestre 4
python src/pipeline.py --calendario
```

También pueden procesarse todos los períodos configurados:

```bash
python src/pipeline.py --todos
```

o todos los trimestres de un año:

```bash
python src/pipeline.py --anio 2025
```

Si se necesita descargar nuevamente un ZIP ya existente:

```bash
python src/pipeline.py --anio 2025 --trimestre 4 --forzar
```

Revisar `results/estado_periodos.csv`, `validacion_publicacion_<periodo>.json`, los CSV y sus `.meta.json`. Un período `FALLIDO` no reemplaza el histórico vigente.

### Qué informa el calendario

`python src/pipeline.py --calendario` **no consulta INDEC en línea**. Muestra la fecha esperada y el estado local.

Antes de procesar un período `SIN PROCESAR`, usar:

```bash
python src/monitor_actualizaciones.py
```

para confirmar que el ZIP oficial esté realmente disponible.

El calendario distingue entre:

- `FUTURO`: todavía no corresponde esperar el período;
- `SIN PROCESAR`: ya se alcanzó la fecha esperada, pero no existe un estado local procesado;
- `VALIDADO`: el período superó los controles definidos por el proyecto;
- `PUBLICADO`: el período fue incorporado a la salida publicada.

## Monitor de nuevas publicaciones

```bash
python src/monitor_actualizaciones.py
python src/monitor_actualizaciones.py --prevalidar
```

También puede prevalidarse un período de forma explícita:

```bash
python src/monitor_actualizaciones.py --anio 2026 --trimestre 2 --prevalidar
```

La prevalidación escribe en `results/monitor_actualizaciones/` y no incorpora el trimestre al histórico.

El monitor comprueba que el recurso encontrado sea un ZIP válido y utilizable; una respuesta HTTP 200 por sí sola no se interpreta como una publicación válida.

Las alertas son operativas y no constituyen pruebas de significancia estadística.

## Preparar el snapshot

Sólo después de revisar un período `VALIDADO`:

```bash
python src/pipeline.py --publicar-snapshot
```

El comando actualiza `data_snapshot/`, excluye microdatos individuales y no despliega la aplicación en la nube.

En V3.5.0 el snapshot versionado cubre **13 períodos**, desde `2023T1` hasta `2026T1`, e incluye las salidas agregadas y segmentadas necesarias para el portal.

## Abrir el portal

```bash
python -m streamlit run portal/app.py
```

La V3.5.0 presenta nueve secciones:

1. **Resumen ejecutivo**
2. **Evolución laboral**
3. **Presión laboral**
4. **Brechas y perfiles**
5. **Ingresos**
6. **Calendario**
7. **Calidad y auditoría**
8. **Documentación y descargas**
9. **Administración**

La sección **Presión laboral** incorpora también la lectura de horas e intensidad laboral.

Si `results/` no tiene un último período `VALIDADO` o `PUBLICADO`, la aplicación conserva el último `data_snapshot/` válido.

## Validación metodológica

En **Calidad y auditoría** se muestra el contraste contra INDEC.

### Tasas principales

El cierre V3.5.0 mantiene **27/27 concordancias** para actividad, empleo y desocupación en 9 trimestres (`2024T1`–`2026T1`).

La evidencia se encuentra en `docs/validacion_metodologica_indec.csv` y la matriz en `docs/MATRIZ_VALIDACION_METODOLOGICA.md`.

Para regenerar el contraste:

```bash
python scripts/validar_contra_indec.py
```

### Presión sobre el mercado de trabajo

La V3.5.0 incorpora:

- ocupados demandantes;
- subocupación horaria;
- subocupación demandante;
- subocupación no demandante.

La validación externa cubre los 13 períodos `2023T1`–`2026T1` y registra **52/52 concordancias**.

Para regenerarla:

```bash
python scripts/validar_presion_laboral_indec.py
```

La referencia utilizada se encuentra en:

```text
docs/referencia_indec_presion_laboral.csv
```

## Horas trabajadas e intensidad laboral

La V3.5.0 incorpora:

- horas semanales totales (`PP3E_TOT + PP3F_TOT`);
- promedio semanal ponderado;
- mediana semanal ponderada;
- sobreocupación horaria;
- controles de consistencia con `INTENSI`.

Para ejecutar el diagnóstico:

```bash
python scripts/diagnosticar_horas_trabajadas.py
```

Para validar la consistencia interna:

```bash
python scripts/validar_horas_intensidad.py
```

La consistencia fue revisada para los 13 períodos del histórico.

La sobreocupación **no se presenta como concordancia externa por aglomerado**, porque la referencia utilizada no publica un valor compatible con ese nivel de desagregación.

## Análisis segmentado

La V3.5.0 mantiene los análisis por sexo, edad, nivel educativo y deciles de ingreso, e incorpora el cruce:

```text
Edad × Nivel educativo
```

Grupos de edad:

- `14–29`
- `30–64`
- `65+`

El cruce utiliza los siete niveles educativos disponibles en la EPH.

Para regenerar los análisis segmentados históricos:

```bash
python scripts/generar_segmentados_historicos.py
```

El portal muestra el tamaño muestral junto a los resultados.

Los grupos con `n < 10` permanecen visibles, pero se excluyen de la identificación automática de máximos y mínimos.

Estos umbrales son ayudas de lectura del portal y **no constituyen reglas oficiales de precisión estadística del INDEC**.

## Ponderadores y lectura

- Tasas laborales, expansiones, presión laboral e informalidad: `PONDERA`.
- Ingreso ponderado `P21`: `PONDIIO`; no se sustituye por `PONDERA` cuando falta.
- Deciles: `ADECOCUR` cuando está disponible.
- Tasas específicas 14+: implementadas, testeadas y utilizadas como referencia específica.
- Tasas 10+: referencia histórica complementaria.
- Ingresos: pesos corrientes; para analizar poder adquisitivo deben deflactarse.
- Brechas y variaciones: descriptivas; no equivalen automáticamente a significancia estadística.
- Las lecturas automáticas del portal describen cambios observados y no prueban causalidad.

## Ejecutar los tests

Desde la raíz del repositorio:

```bash
python -m pytest tests -q
```

Resultado de cierre de V3.5.0:

```text
101 passed
```

Si una prueba falla, no se recomienda publicar un nuevo snapshot hasta revisar el problema.

## Flujo recomendado para un período nuevo

1. Consultar el monitor.
2. Prevalidar el nuevo período.
3. Revisar alertas y estructura.
4. Procesarlo con `src/pipeline.py`.
5. Revisar resultados y metadatos.
6. Ejecutar la suite de tests.
7. Ejecutar las validaciones metodológicas disponibles.
8. Publicar el snapshot.
9. Revisar el portal.
10. Versionar los cambios con Git.

Ejemplo:

```bash
python src/monitor_actualizaciones.py
python src/monitor_actualizaciones.py --anio 2026 --trimestre 2 --prevalidar
python src/pipeline.py --anio 2026 --trimestre 2
python -m pytest tests -q
python scripts/validar_contra_indec.py
python scripts/validar_presion_laboral_indec.py
python scripts/validar_horas_intensidad.py
python src/pipeline.py --publicar-snapshot
python -m streamlit run portal/app.py
```

Las validaciones contra referencias externas sólo pueden evaluar períodos para los que exista una referencia compatible disponible.

## Ante una falla

1. Leer el mensaje de `estado_periodos.csv`.
2. Revisar el último archivo de `logs/`.
3. Consultar la validación de esquema.
4. Corregir sin borrar el histórico ni el snapshot válidos.
5. Reprocesar y comprobar estado `VALIDADO`.
6. Ejecutar nuevamente los tests antes de publicar.

Si Streamlit está ejecutándose y la terminal no permite escribir, detenerlo con:

```text
Ctrl + C
```

o abrir una segunda terminal y volver a activar el entorno virtual.

## Validación de cierre V3.5.0

- Snapshot versionado: **13 períodos**, `2023T1`–`2026T1`.
- Suite automatizada: **101 tests aprobados**.
- Contraste externo tasas principales: **27/27 concordancias**.
- Contraste externo presión laboral: **52/52 concordancias**.
- Horas e intensidad: consistencia interna validada en los 13 períodos.
- Edad × Nivel educativo: análisis regenerado para los 13 períodos.
- Portal: **9 secciones**.
- Comparación territorial NOA/total: **fuera de alcance de esta versión**.
- Informalidad: contraste externo pendiente.
- Control `tasa_no_respuesta_hogar` basado en `REALIZADA`: revisión técnica pendiente antes de su interpretación.

## Alcance institucional

Los microdatos son producidos por el **INDEC**.

Los indicadores son calculados por este proyecto a partir de la EPH para el **Aglomerado 18 — Santiago del Estero–La Banda**.

El estado `VALIDADO` significa que el resultado superó los controles definidos por el proyecto. No implica certificación oficial por parte del INDEC ni de la DGEyC.

El portal es una herramienta técnica y analítica y no constituye, por sí mismo, una publicación oficial institucional.

Los documentos históricos de versiones anteriores se conservan sin reescribir retroactivamente sus cifras.
