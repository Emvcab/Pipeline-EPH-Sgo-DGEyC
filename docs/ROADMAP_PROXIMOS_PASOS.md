# Roadmap y próximos pasos — Pipeline EPH

**Versión de referencia:** V3.5.0  
**Ámbito:** Aglomerado 18 — Santiago del Estero–La Banda

## Estado actual

La V3.5.0 cierra una etapa de evolución orientada a profundizar el análisis laboral y mejorar la lectura para usuarios no técnicos.

El proyecto dispone de:

- histórico validado de 13 períodos (`2023T1`–`2026T1`);
- 27/27 concordancias externas de actividad, empleo y desocupación;
- 52/52 concordancias externas de presión laboral;
- horas e intensidad con consistencia interna verificada;
- análisis por sexo, edad, educación, deciles y Edad × Nivel educativo;
- portal de 9 secciones;
- 101 pruebas automatizadas.

## Decisiones de alcance ya tomadas

### Comparación territorial

La comparación Santiago del Estero–La Banda vs. NOA vs. total EPH no se considera necesaria para esta etapa y permanece fuera de alcance.

### Publicación institucional

El portal es una herramienta técnica y analítica. No debe presentarse como publicación oficial del INDEC ni de la DGEyC sin autorización institucional.

### Inferencia

Las brechas y variaciones son descriptivas. El proyecto aún no calcula errores estándar, intervalos de confianza ni significancia estadística asociada al diseño muestral.

## Próximas líneas posibles

### 1. Análisis exploratorio avanzado e insights

Profundizar el uso de microdatos individuales para identificar perfiles de presión laboral, horas, educación, ingresos e informalidad.

### 2. Modelado predictivo, sólo si existe una pregunta concreta

Una línea posible es estudiar qué características están asociadas con que una persona ocupada busque otro empleo.

Un posible target sería `ocupado_demandante`, construido a partir de la condición de ocupado y `PP03J`, evitando utilizar como predictores variables que filtren directamente la respuesta.

Esta línea debería desarrollarse en un entorno exploratorio separado, por ejemplo un notebook/Colab, y no incorporarse al pipeline productivo hasta validar utilidad, metodología y desempeño.

### 3. Salud y migración

Evaluar disponibilidad y calidad de variables antes de incorporarlas. No forman parte de V3.5.0.

### 4. Pobreza e indigencia

Si se desarrolla, debe ser un módulo metodológico separado. No debe mezclarse con las tasas laborales sin documentar fuentes, canastas, ingresos familiares y reglas específicas.

### 5. Inferencia estadística

Evaluar errores estándar, coeficientes de variación e intervalos de confianza compatibles con el diseño de la EPH.

### 6. Informalidad

Buscar una referencia externa compatible para ampliar la validación del indicador.

### 7. `REALIZADA`

Revisar el control interno `tasa_no_respuesta_hogar` antes de comunicarlo como indicador de no respuesta.

### 8. Arquitectura y escalabilidad

Si el volumen, la cantidad de usuarios o la frecuencia de actualización aumentan, evaluar persistencia, separación de servicios, autenticación corporativa y métricas por etapa.

## Principio para nuevas evoluciones

Cada nueva función debe responder:

1. **Qué** se incorpora.
2. **Cómo** se calcula o implementa.
3. **Para qué** sirve.
4. **Por qué** es necesaria.
5. Qué evidencia permite validarla.
6. Qué limitaciones tiene.

La prioridad es preservar trazabilidad, claridad metodológica y utilidad para la toma de decisiones.
