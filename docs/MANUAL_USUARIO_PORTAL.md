# Manual de usuario del portal

**Versión:** V3.5.0  
**Portal:** Mercado laboral en Santiago del Estero–La Banda  
**Fuente:** Encuesta Permanente de Hogares (EPH) — INDEC · Aglomerado 18

Este manual está pensado para personas que consultan el portal sin conocimientos de programación ni estadística avanzada.

## 1. Qué muestra el portal

El portal trabaja con salidas agregadas validadas del Pipeline EPH. Si existen resultados locales cuyo último período está `VALIDADO` o `PUBLICADO`, los prioriza; en caso contrario utiliza el snapshot versionado.

Los microdatos son producidos por el INDEC. Los indicadores del portal son calculados por este proyecto y no constituyen, por sí mismos, una publicación oficial del INDEC ni de la DGEyC.

## 2. Secciones

### Resumen ejecutivo

Permite elegir un período de referencia y otro de comparación. Muestra actividad, empleo, desocupación, población inactiva, tamaño muestral, población expandida e informalidad cuando está disponible. Incluye una explicación pedagógica de los principales conceptos y puede generar un reporte PDF.

### Evolución laboral

Series interactivas para actividad, empleo, desocupación, inactividad e informalidad. Los filtros `Desde` y `Hasta` acotan el rango temporal. La lectura descriptiva resume el cambio entre el primer y el último período seleccionado, además de máximos y mínimos.

### Presión laboral

Incorpora cuatro indicadores:

- ocupados demandantes;
- subocupación;
- subocupación demandante;
- subocupación no demandante.

La sección también presenta horas trabajadas e intensidad laboral, incluido el promedio y la mediana semanal y la sobreocupación.

La idea central es que una desocupación baja no resume por sí sola toda la presión del mercado de trabajo.

### Brechas y perfiles

Presenta análisis por sexo, edad, nivel educativo, deciles de ingreso y el cruce **Edad × Nivel educativo**.

El portal muestra `n_muestra` y población expandida. Los grupos con menos de 10 casos permanecen visibles, pero se excluyen de la identificación automática de máximos y mínimos.

Las advertencias de tamaño muestral son ayudas de lectura y no reglas oficiales de precisión del INDEC.

### Ingresos

Muestra ingreso promedio ponderado, ingreso mediano y no respuesta de ingresos. El promedio ponderado de `P21` utiliza `PONDIIO`.

Los montos son pesos corrientes. Una suba nominal no implica necesariamente una mejora del poder adquisitivo.

### Calendario

Muestra fechas esperadas y estados locales. No confirma por sí solo que el ZIP oficial ya esté disponible; esa comprobación la realiza el monitor.

### Calidad y auditoría

Incluye estados de períodos, controles de calidad, validación de esquema y evidencia metodológica.

Al cierre V3.5.0:

- tasas principales: **27/27 concordancias** contra INDEC;
- presión laboral: **52/52 concordancias** contra referencias publicadas;
- horas e intensidad: consistencia interna verificada en 13 períodos.

### Documentación y descargas

Centraliza histórico, indicadores, calidad, estados, metadatos, manifiesto, evidencia metodológica y guías.

### Administración

Área protegida para consultar INDEC, prevalidar períodos y, únicamente cuando las escrituras están habilitadas y existe confirmación humana, incorporar un trimestre mediante el pipeline transaccional.

## 3. Indicadores y ponderadores

| Elemento | Regla V3.5.0 |
|---|---|
| Tasas laborales principales | `PONDERA` |
| Tasas específicas 14+ | `PONDERA` |
| Presión laboral | `PONDERA`, denominador PEA |
| Informalidad | `PONDERA`; contraste externo pendiente |
| Ingreso ponderado `P21` | `PONDIIO` |
| Deciles de ingreso | `ADECOCUR` + `PONDIIO` cuando están disponibles |
| Horas trabajadas | `PP3E_TOT + PP3F_TOT` |
| Sobreocupación | `INTENSI = 3` |

## 4. Cómo interpretar responsablemente

- Una desocupación baja no debe interpretarse de manera aislada; conviene mirar empleo, actividad, inactividad, presión laboral, horas e informalidad.
- Una diferencia entre períodos o grupos es descriptiva. La versión actual no calcula errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral.
- Las lecturas automáticas no prueban causalidad.
- Los ingresos son nominales.
- El Aglomerado 18 reúne Santiago del Estero y La Banda; no representa automáticamente a toda la provincia y los microdatos públicos no permiten separar ambas ciudades.
- La comparación territorial con NOA o total EPH no forma parte de V3.5.0.
- El control interno `tasa_no_respuesta_hogar` basado en `REALIZADA` continúa pendiente de revisión técnica antes de interpretarse.

## 5. Descargas y trazabilidad

Los CSV se acompañan de metadatos `.meta.json` cuando corresponde. Para reutilizar una salida conviene conservar el archivo junto con su metadata.

La matriz metodológica, la evidencia de tasas principales y la referencia de presión laboral documentan el estado de validación de V3.5.0.

Ante dudas sobre fórmulas, consultar [METODOLOGIA.md](METODOLOGIA.md). Para operación desde consola, consultar [GUIA_USO.md](GUIA_USO.md).
