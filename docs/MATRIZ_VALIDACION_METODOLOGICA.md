# Matriz de validación metodológica de indicadores

**Estado de cierre:** V3.4.0

## Objetivo

Documentar la correspondencia entre los indicadores calculados por el Pipeline EPH y los universos, variables, ponderadores y fórmulas utilizados para su construcción.

## Clasificación de indicadores

### 1. Indicadores principales

- **Tasa de actividad:** PEA expandida / población total expandida × 100.
- **Tasa de empleo:** ocupados expandidos / población total expandida × 100.
- **Tasa de desocupación:** desocupados expandidos / PEA expandida × 100.

Ponderador: `PONDERA`.

### 2. Indicadores específicos de 14 años y más

- **Tasa de actividad 14+:** PEA 14+ / población 14+ × 100.
- **Tasa de empleo 14+:** ocupados 14+ / población 14+ × 100.
- **Tasa de desocupación 14+:** desocupados 14+ / PEA 14+ × 100.

Ponderador: `PONDERA`. Estado: **implementadas y testeadas**.

### 3. Indicadores complementarios de referencia histórica

- **Tasa de actividad 10 años y más.**
- **Tasa de empleo 10 años y más.**
- **Tasa de inactividad 10 años y más.**

Se conservan por trazabilidad histórica y análisis complementario. No sustituyen las tasas específicas 14+.

## Ingresos y deciles

- `P21` ponderado: `suma(P21 × PONDIIO) / suma(PONDIIO)` entre ocupados con `P21 > 0` y `PONDIIO > 0`.
- Si `PONDIIO` no está disponible, no se usa `PONDERA` como reemplazo silencioso.
- Los deciles utilizan `ADECOCUR` cuando está disponible; no se fabrican deciles locales alternativos.

Estos criterios quedaron **verificados, implementados y testeados en V3.4.0**.

## Informalidad

La informalidad se calcula sobre ocupados con `EMPLEO` válido usando `PONDERA`. La implementación está disponible; el contraste externo equivalente permanece pendiente.

## Alcance inferencial

Las estimaciones y brechas del portal son descriptivas. La V3.4.0 no calcula errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral. Las diferencias observadas no deben interpretarse automáticamente como estadísticamente significativas ni causales.

## Validación empírica contra publicaciones oficiales del INDEC

Se contrastaron las tasas principales del Aglomerado 18 — Santiago del Estero–La Banda para nueve trimestres consecutivos (`2024T1`–`2026T1`). Para cada período se compararon actividad, empleo y desocupación, totalizando **27 comparaciones**.

### Resultado

**27 de 27 comparaciones concordaron con los valores publicados por INDEC al nivel de redondeo de una cifra decimal utilizado en los informes verificados.**

| Indicador / componente | Estado metodológico al cierre V3.4.0 |
|---|---|
| Tasa de actividad principal | VALIDADA Y REPRODUCIDA |
| Tasa de empleo principal | VALIDADA Y REPRODUCIDA |
| Tasa de desocupación principal | VALIDADA Y REPRODUCIDA |
| Tasas específicas 14+ | IMPLEMENTADAS Y TESTEADAS |
| Tasas 10+ | COMPLEMENTARIAS DE REFERENCIA HISTÓRICA |
| Ingreso P21 con PONDIIO | IMPLEMENTADO Y TESTEADO |
| Deciles mediante ADECOCUR | IMPLEMENTACIÓN CONCORDANTE |
| Informalidad laboral | CONTRASTE EXTERNO PENDIENTE |
| `tasa_no_respuesta_hogar` / `REALIZADA` | REVISIÓN TÉCNICA PENDIENTE ANTES DE INTERPRETAR |
| Errores estándar / intervalos / significancia | NO IMPLEMENTADO EN V3.4.0 |
| Comparación territorial NOA / total EPH | FUERA DE ALCANCE DEL CIERRE V3.4.0 |

La evidencia detallada se conserva en `docs/validacion_metodologica_indec.csv`. La comparación puede regenerarse con:

```bash
python scripts/validar_contra_indec.py
```

La reproducción de los valores publicados no implica certificación formal por parte del INDEC ni de la DGEyC.
