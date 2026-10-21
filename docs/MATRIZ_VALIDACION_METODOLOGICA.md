# Matriz de validación metodológica de indicadores

**Estado de cierre:** V3.5.0

## Objetivo

Documentar la correspondencia entre los indicadores calculados por el Pipeline EPH y los universos, variables, ponderadores, fórmulas y evidencias utilizadas para su validación.

## Indicadores principales

- **Tasa de actividad:** PEA expandida / población total expandida × 100.
- **Tasa de empleo:** ocupados expandidos / población total expandida × 100.
- **Tasa de desocupación:** desocupados expandidos / PEA expandida × 100.

Ponderador: `PONDERA`.

Validación externa: **27/27 concordancias** para 9 trimestres (`2024T1`–`2026T1`) al nivel de redondeo publicado por INDEC.

## Tasas específicas de 14 años y más

- tasa de actividad 14+;
- tasa de empleo 14+;
- tasa de desocupación 14+.

Ponderador: `PONDERA`. Estado: **implementadas y testeadas**.

Las tasas 10+ se conservan como referencia histórica complementaria.

## Presión sobre el mercado de trabajo

Universo y reglas:

- ocupados demandantes: `ESTADO = 1` y `PP03J = 1`;
- subocupación: `ESTADO = 1` e `INTENSI = 1`;
- subocupación demandante: `ESTADO = 1`, `INTENSI = 1` y `PP03J = 1`;
- subocupación no demandante: `ESTADO = 1`, `INTENSI = 1` y `PP03J = 2`.

Denominador: PEA.  
Ponderador: `PONDERA`.

Validación externa: **52/52 concordancias** para 13 períodos (`2023T1`–`2026T1`) y 4 indicadores.

Referencia: `docs/referencia_indec_presion_laboral.csv`.

## Horas e intensidad laboral

- horas semanales: `PP3E_TOT + PP3F_TOT`;
- subocupación: `INTENSI = 1`;
- sobreocupación: `INTENSI = 3`, asociada a jornadas superiores a 45 horas semanales;
- se calculan promedio y mediana semanal ponderados.

Estado: **consistencia interna validada en los 13 períodos**.

No se afirma una concordancia numérica externa de sobreocupación por aglomerado, porque la referencia utilizada no publica un valor compatible con ese nivel de desagregación.

## Ingresos y deciles

- `P21` ponderado: `suma(P21 × PONDIIO) / suma(PONDIIO)` entre ocupados con `P21 > 0` y `PONDIIO > 0`.
- Si `PONDIIO` no está disponible, no se usa `PONDERA` como reemplazo silencioso.
- Los deciles utilizan `ADECOCUR` cuando está disponible; no se fabrican deciles locales alternativos.

Estado: **implementado y testeado**.

## Informalidad

La informalidad se calcula sobre ocupados con `EMPLEO` válido usando `PONDERA`.

Estado: **implementada; contraste externo equivalente pendiente**.

## Análisis segmentado

Dimensiones:

- Sexo;
- Edad: 14–29, 30–64, 65+;
- Nivel educativo;
- Edad × Nivel educativo;
- Decil de ingreso.

El cruce Edad × Nivel educativo se verificó estructuralmente para los 13 períodos. El portal muestra tamaño muestral y población expandida.

Los umbrales de lectura (`n < 10`, `10–29`, `n >= 30`) son ayudas operativas y no reglas oficiales de precisión estadística del INDEC.

## Alcance inferencial

La V3.5.0 no calcula errores estándar, intervalos de confianza ni pruebas de hipótesis asociadas al diseño muestral.

Las diferencias observadas son descriptivas y no deben interpretarse automáticamente como estadísticamente significativas ni causales.

## Estado resumido

| Indicador / componente | Estado al cierre V3.5.0 |
|---|---|
| Tasa de actividad principal | VALIDADA Y REPRODUCIDA |
| Tasa de empleo principal | VALIDADA Y REPRODUCIDA |
| Tasa de desocupación principal | VALIDADA Y REPRODUCIDA |
| Tasas específicas 14+ | IMPLEMENTADAS Y TESTEADAS |
| Tasas 10+ | REFERENCIA HISTÓRICA COMPLEMENTARIA |
| Presión laboral | VALIDADA EXTERNAMENTE · 52/52 |
| Horas e intensidad | VALIDACIÓN INTERNA · 13/13 PERÍODOS |
| Sobreocupación externa por aglomerado | SIN REFERENCIA NUMÉRICA COMPATIBLE |
| Ingreso P21 con PONDIIO | IMPLEMENTADO Y TESTEADO |
| Deciles mediante ADECOCUR | IMPLEMENTACIÓN CONCORDANTE |
| Edad × Nivel educativo | IMPLEMENTADO Y VERIFICADO · 13 PERÍODOS |
| Informalidad laboral | CONTRASTE EXTERNO PENDIENTE |
| `tasa_no_respuesta_hogar` / `REALIZADA` | REVISIÓN TÉCNICA PENDIENTE |
| Errores estándar / intervalos / significancia | NO IMPLEMENTADO |
| Comparación territorial NOA / total EPH | FUERA DE ALCANCE |

## Evidencia y comandos

Tasas principales:

```bash
python scripts/validar_contra_indec.py
```

Presión laboral:

```bash
python scripts/validar_presion_laboral_indec.py
```

Horas e intensidad:

```bash
python scripts/validar_horas_intensidad.py
```

La reproducción de valores publicados no implica certificación formal por parte del INDEC ni de la DGEyC.
