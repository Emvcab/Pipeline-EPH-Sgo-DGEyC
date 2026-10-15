# Metodología de indicadores

**Versión de referencia:** V3.4.0  
**Ámbito:** Aglomerado 18 — Santiago del Estero - La Banda  
**Fuente:** microdatos públicos de la Encuesta Permanente de Hogares (EPH), INDEC

## Universo y ponderación

El procesamiento filtra `AGLOMERADO = 18`. Para las expansiones poblacionales, tasas laborales e informalidad se utiliza `PONDERA`. El ingreso de la ocupación principal `P21` utiliza `PONDIIO`, el ponderador específico de ingreso. No se imputan faltantes ni se convierten en cero.

## Indicadores principales

```text
tasa_actividad_oficial = PEA expandida / población total expandida × 100
tasa_empleo_oficial = ocupados expandidos / población total expandida × 100
tasa_desocupacion = desocupados expandidos / PEA expandida × 100
proporcion_inactiva_total = 100 - tasa_actividad_oficial
```

Las tasas principales reproducen la formulación utilizada para el contraste con las publicaciones oficiales del Aglomerado 18. La proporción inactiva total es complementaria y no equivale a una tasa específica por edad.

## Tasas específicas de 14 años y más

```text
tasa_actividad_14_mas = PEA 14+ expandida / población 14+ expandida × 100
tasa_empleo_14_mas = ocupados 14+ expandidos / población 14+ expandida × 100
tasa_desocupacion_14_mas = desocupados 14+ expandidos / PEA 14+ expandida × 100
```

Estas tasas utilizan `PONDERA` y constituyen la referencia específica vigente incorporada en V3.4.0.

## Indicadores de 10 años y más

```text
tasa_actividad_10_mas = PEA expandida / población de 10 años y más expandida × 100
tasa_empleo_10_mas = ocupados expandidos / población de 10 años y más expandida × 100
tasa_inactividad_10_mas = inactivos expandidos / población de 10 años y más expandida × 100
```

Se conservan para trazabilidad histórica y análisis complementario. No deben presentarse como sustitutos de las tasas específicas 14+.

## Informalidad

La tasa de informalidad se calcula como ocupados ponderados con `EMPLEO = 2` sobre ocupados ponderados con `EMPLEO` en `{1, 2}`, multiplicado por 100 y utilizando `PONDERA`. En `2023T1`, `2023T2` y `2023T3` la variable necesaria no está disponible; el indicador queda como no disponible y no se imputa.

El cálculo está implementado, pero su contraste contra una referencia externa equivalente permanece pendiente.

## Ingreso de la ocupación principal

Para ocupados con `P21 > 0`, el promedio ponderado se calcula como:

```text
suma(P21 × PONDIIO) / suma(PONDIIO)
```

Sólo intervienen registros con `PONDIIO` válido y positivo. Si `PONDIIO` no está disponible, el promedio ponderado queda sin estimar; **no se sustituye silenciosamente por `PONDERA`**. El promedio simple y la mediana observada de `P21` se conservan como medidas descriptivas adicionales. Todos los montos son pesos argentinos nominales y requieren deflactación para estudiar poder adquisitivo.

## Deciles de ingreso

Cuando la base incluye `ADECOCUR` y `PONDIIO`, se utiliza la escala decílica publicada por INDEC para el ingreso de la ocupación principal. No se construyen deciles locales alternativos cuando `ADECOCUR` no está disponible.

## Análisis segmentado

La capa incorporada en V3.3 y vigente en V3.4 genera salidas adicionales para el Aglomerado 18 sin modificar las tasas agregadas históricas:

- **Sexo:** tasas de actividad, empleo y desocupación para población de 14 años y más; `CH04=1` varón y `CH04=2` mujer.
- **Edad:** grupos de 14 a 29 años, 30 a 64 años y 65 años y más.
- **Nivel educativo:** `NIVEL_ED` (o `NIVELED` por compatibilidad histórica); se excluye `9=Ns/Nr` de las categorías publicadas.
- **Deciles de ingreso:** `ADECOCUR` y `PONDIIO` cuando están disponibles.

Las lecturas automáticas de brechas son estrictamente descriptivas.

## Validación metodológica contra INDEC

Las tasas principales fueron contrastadas con publicaciones oficiales del INDEC para 9 trimestres consecutivos, desde `2024T1` hasta `2026T1`. Se compararon actividad, empleo y desocupación: **27 de 27 comparaciones concordaron** al nivel de redondeo de una cifra decimal utilizado en los informes verificados.

La evidencia se conserva en `docs/validacion_metodologica_indec.csv` y puede regenerarse con:

```bash
python scripts/validar_contra_indec.py
```

Esta concordancia demuestra reproducción de los valores publicados en el conjunto verificado; no constituye certificación formal del INDEC ni de la DGEyC.

## Alcance inferencial

La EPH es una encuesta por muestreo. La V3.4.0 no estima errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral. Una diferencia entre períodos o grupos puede describirse en puntos porcentuales, pero no debe interpretarse automáticamente como estadísticamente significativa. El sistema tampoco atribuye causalidad.

## Alcance territorial

El proyecto se mantiene centrado en el **Aglomerado 18 — Santiago del Estero–La Banda**. Los microdatos públicos no permiten separar ambas ciudades. La comparación con NOA o con el total de aglomerados no forma parte del cierre V3.4.0.

## Punto técnico pendiente: `REALIZADA`

El pipeline conserva un control interno denominado `tasa_no_respuesta_hogar` que actualmente busca `REALIZADA = 0`. La documentación de diseño de registro utilizada por el proyecto identifica `REALIZADA = 1` como entrevista realizada y `REALIZADA = 2` como no realizada. Por lo tanto, este control debe revisarse antes de utilizarse o comunicarse como indicador de no respuesta de hogares. No afecta las 27 comparaciones de actividad, empleo y desocupación validadas contra INDEC.

## Otras limitaciones

- Los microdatos públicos no permiten evaluar encuestadores ni personal de carga.
- Los resultados calculados no sustituyen procedimientos institucionales confirmados.
- Machine Learning sólo debería evaluarse en una etapa posterior, una vez definido un problema institucional concreto, con datos suficientes y validación metodológica.

## Antecedente documental

`Reporte_Ejecutivo_EPH_SDE_4T2025.pdf` conserva cifras y textos producidos en una etapa anterior. Se mantiene como antecedente histórico y no define la metodología vigente de V3.4.0.
