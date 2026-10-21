# Manual de usuario del portal

**Versión:** V3.4.0  
**Tablero:** Mercado laboral en Santiago del Estero - La Banda  
**Fuente:** Encuesta Permanente de Hogares (EPH) — INDEC · Aglomerado 18

Este manual está pensado para personas que consultan el portal sin conocimientos de programación ni estadística avanzada.

## 1. Qué muestra el portal

El portal trabaja con salidas agregadas validadas del Pipeline EPH. Si existen resultados locales con último período `VALIDADO` o `PUBLICADO`, los prioriza; en caso contrario usa el snapshot versionado. Los resultados no constituyen una nueva estadística oficial provincial.

## 2. Secciones

### Resumen ejecutivo

Permite elegir un período de referencia y otro de comparación. Muestra actividad, empleo, desocupación, inactividad, muestra, población expandida e informalidad cuando está disponible. Las diferencias se expresan de forma descriptiva en puntos porcentuales. También permite descargar un reporte PDF institucional del período.

### Evolución laboral

Series interactivas con Plotly para actividad, empleo, desocupación, inactividad e informalidad. Los filtros `Desde` y `Hasta` acotan el rango temporal; hover y zoom facilitan la lectura.

### Brechas y perfiles

Presenta análisis por sexo, grupos de edad y nivel educativo, además de ingresos por deciles cuando `ADECOCUR` y `PONDIIO` están disponibles. Las lecturas automáticas identifican máximos, mínimos y brechas, pero no prueban causalidad ni significancia estadística.

### Ingresos

Muestra ingreso promedio ponderado, ingreso mediano y no respuesta de ingresos. El promedio ponderado de `P21` usa `PONDIIO`. Los montos son pesos corrientes; para estudiar poder adquisitivo deben deflactarse.

### Calendario

Muestra fechas esperadas y estados locales. El calendario no confirma por sí solo que el ZIP oficial ya esté disponible; esa comprobación la realiza el monitor.

### Calidad y auditoría

Incluye estados de períodos, controles de calidad, validación de esquema y el bloque **Validación metodológica contra INDEC**. El cierre V3.4.0 registra **27/27 concordancias** para actividad, empleo y desocupación en 9 trimestres (`2024T1`–`2026T1`). Desde esta sección se puede descargar la evidencia y la matriz metodológica.

### Documentación y descargas

Centraliza histórico, indicadores, calidad, estados, metadatos, manifiesto, validación de esquema y guías.

### Administración

Área protegida para consultar INDEC, prevalidar períodos y, sólo cuando las escrituras están habilitadas y existe confirmación humana, incorporar un trimestre mediante el pipeline transaccional.

## 3. Indicadores y ponderadores

| Elemento | Regla de V3.4.0 |
|---|---|
| Tasas principales | `PONDERA` |
| Tasas específicas 14+ | `PONDERA` |
| Tasas 10+ | Referencia histórica complementaria |
| Informalidad | `PONDERA`; contraste externo pendiente |
| Ingreso ponderado `P21` | `PONDIIO` |
| Deciles de ingreso | `ADECOCUR` + `PONDIIO` cuando están disponibles |

## 4. Cómo interpretar responsablemente

- Una desocupación baja no debe interpretarse de manera aislada; conviene mirar actividad, empleo, inactividad e informalidad.
- Una diferencia entre períodos o grupos es descriptiva. La versión actual no calcula errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral.
- Los ingresos son nominales.
- El Aglomerado 18 reúne Santiago del Estero y La Banda; los microdatos públicos no permiten separar ambas ciudades.
- La comparación territorial con NOA o total EPH no forma parte del cierre V3.4.0.
- El control interno `tasa_no_respuesta_hogar` basado en `REALIZADA` debe revisarse antes de interpretarse como indicador de no respuesta.

## 5. Descargas y trazabilidad

Los CSV se acompañan de metadatos `.meta.json` cuando corresponde. Para reutilizar una salida, conviene conservar el archivo junto con su metadata. La matriz metodológica y el CSV de validación contra INDEC documentan el estado de los indicadores al cierre de V3.4.0.

Ante cualquier duda sobre fórmulas, el documento de referencia es [METODOLOGIA.md](METODOLOGIA.md).
