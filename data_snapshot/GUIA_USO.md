# Guía de uso

**Versión de referencia:** V3.4.0

## Procesar

Desde la raíz del repositorio:

```bash
python src/pipeline.py --anio 2025 --trimestre 4
python src/pipeline.py --calendario
```

Revisar `results/estado_periodos.csv`, `validacion_publicacion_<periodo>.json`, los CSV y sus `.meta.json`. Un período `FALLIDO` no reemplaza el histórico vigente.

### Qué informa el calendario

`python src/pipeline.py --calendario` **no consulta INDEC en línea**. Muestra la fecha esperada y el estado local. Antes de procesar un `SIN PROCESAR`, usar `python src/monitor_actualizaciones.py` para confirmar que el ZIP oficial esté realmente disponible.

## Monitor de nuevas publicaciones

```bash
python src/monitor_actualizaciones.py
python src/monitor_actualizaciones.py --prevalidar
```

La prevalidación escribe en `results/monitor_actualizaciones/` y no incorpora el trimestre al histórico. Las alertas son operativas y no constituyen pruebas de significancia estadística.

## Preparar el snapshot

Sólo después de revisar un período `VALIDADO`:

```bash
python src/pipeline.py --publicar-snapshot
```

El comando excluye microdatos y no despliega la aplicación en la nube.

## Abrir el portal

```bash
python -m streamlit run portal/app.py
```

La V3.4.0 presenta ocho secciones: **Resumen ejecutivo, Evolución laboral, Brechas y perfiles, Ingresos, Calendario, Calidad y auditoría, Documentación y descargas, y Administración**. Si `results/` no tiene un último período validado, la aplicación usa `data_snapshot/`.

## Validación metodológica

En **Calidad y auditoría** se muestra el contraste contra INDEC. El cierre V3.4.0 registra **27/27 concordancias** para actividad, empleo y desocupación en 9 trimestres (`2024T1`–`2026T1`). La evidencia se encuentra en `docs/validacion_metodologica_indec.csv` y la matriz en `docs/MATRIZ_VALIDACION_METODOLOGICA.md`.

Para regenerar el contraste:

```bash
python scripts/validar_contra_indec.py
```

## Ponderadores y lectura

- Tasas laborales, expansiones e informalidad: `PONDERA`.
- Ingreso ponderado `P21`: `PONDIIO`; no se sustituye por `PONDERA` cuando falta.
- Deciles: `ADECOCUR` cuando está disponible.
- Tasas específicas 14+: implementadas y testeadas.
- Tasas 10+: referencia histórica complementaria.
- Ingresos: pesos corrientes; para poder adquisitivo deben deflactarse.
- Brechas y variaciones: descriptivas; no equivalen automáticamente a significancia estadística.

## Ante una falla

1. Leer el mensaje de `estado_periodos.csv`.
2. Revisar el último archivo de `logs/`.
3. Consultar la validación de esquema.
4. Corregir sin borrar el histórico ni el snapshot válidos.
5. Reprocesar y comprobar estado `VALIDADO`.

## Validación de cierre V3.4.0

- Snapshot versionado: **13 períodos**, `2023T1`–`2026T1`.
- Suite automatizada: **97 tests aprobados**.
- Contraste externo tasas principales: **27/27 concordancias**.
- Comparación territorial NOA/total: **fuera de alcance de esta versión**.
- Informalidad: contraste externo pendiente.
- Control `tasa_no_respuesta_hogar` basado en `REALIZADA`: revisión técnica pendiente antes de su interpretación.

Los documentos históricos de versiones anteriores se conservan sin reescribir retroactivamente sus cifras.
