# Diccionario de datos

**Fuente:** Encuesta Permanente de Hogares — microdatos públicos del INDEC
**Ámbito:** Aglomerado 18 — Santiago del Estero–La Banda
**Ponderadores:** `PONDERA` para tasas/expansiones generales e informalidad; `PONDIIO` para el promedio ponderado de `P21`

## Histórico e indicadores trimestrales

`historico_SDE.csv` contiene una fila por período validado. `indicadores_SDE_<periodo>.csv` contiene la misma estructura para un único trimestre.

| Variable | Tipo | Definición / fórmula | Unidad |
|---|---|---|---|
| `anio` | entero | Año del relevamiento | año |
| `trimestre` | entero | Trimestre 1 a 4 | trimestre |
| `periodo` | texto | Formato `AAAATn` | período |
| `aglomerado` | entero | Código 18 | código |
| `n_personas_muestra` | entero | Personas observadas | personas de muestra |
| `n_hogares_muestra` | entero | Hogares observados | hogares de muestra |
| `poblacion_expandida_total` | entero | Suma de `PONDERA` de todas las personas del aglomerado | personas expandidas |
| `poblacion_expandida_mayor10` | entero | Suma de `PONDERA` con `CH06 >= 10` | personas expandidas |
| `poblacion_expandida_14_mas` | entero | Suma de `PONDERA` con `CH06 >= 14` | personas expandidas |
| `pea_expandida_14_mas` | entero | Suma de `PONDERA` con `CH06 >= 14` y `ESTADO` 1 o 2 | personas expandidas |
| `ocupados_expandidos_14_mas` | entero | Suma de `PONDERA` con `CH06 >= 14` y `ESTADO = 1` | personas expandidas |
| `desocupados_expandidos_14_mas` | entero | Suma de `PONDERA` con `CH06 >= 14` y `ESTADO = 2` | personas expandidas |
| `pea_expandida` | entero | Suma de `PONDERA` con `ESTADO` 1 o 2 | personas expandidas |
| `ocupados_expandidos` | entero | Suma de `PONDERA` con `ESTADO = 1` | personas expandidas |
| `desocupados_expandidos` | entero | Suma de `PONDERA` con `ESTADO = 2` | personas expandidas |
| `inactivos_expandidos` | entero | Suma de `PONDERA` con `ESTADO = 3` | personas expandidas |
| `tasa_actividad_oficial` | decimal | PEA expandida / población total expandida × 100 | porcentaje |
| `tasa_empleo_oficial` | decimal | ocupados expandidos / población total expandida × 100 | porcentaje |
| `tasa_desocupacion` | decimal | desocupados expandidos / PEA expandida × 100 | porcentaje |
| `proporcion_inactiva_total` | decimal | 100 - `tasa_actividad_oficial` | porcentaje |
| `tasa_actividad_10_mas` | decimal | PEA expandida / población de 10 años y más expandida × 100 | porcentaje |
| `tasa_empleo_10_mas` | decimal | ocupados expandidos / población de 10 años y más expandida × 100 | porcentaje |
| `tasa_inactividad_10_mas` | decimal | inactivos expandidos / población de 10 años y más expandida × 100 | porcentaje |
| `tasa_actividad_14_mas` | decimal | PEA 14+ expandida / población 14+ expandida × 100 | porcentaje |
| `tasa_empleo_14_mas` | decimal | ocupados 14+ expandidos / población 14+ expandida × 100 | porcentaje |
| `tasa_desocupacion_14_mas` | decimal | desocupados 14+ expandidos / PEA 14+ expandida × 100 | porcentaje |
| `tasa_informalidad` | decimal o nulo | EMPLEO=2 ponderado / EMPLEO válido 1 o 2 ponderado × 100 | porcentaje |
| `tasa_ocupados_demandantes` | decimal o nulo | Ocupados con `PP03J = 1`, ponderados / PEA ponderada × 100 | porcentaje |
| `tasa_subocupacion` | decimal o nulo | Ocupados con `INTENSI = 1`, ponderados / PEA ponderada × 100 | porcentaje |
| `tasa_subocupacion_demandante` | decimal o nulo | Ocupados con `INTENSI = 1` y `PP03J = 1`, ponderados / PEA ponderada × 100 | porcentaje |
| `tasa_subocupacion_no_demandante` | decimal o nulo | Ocupados con `INTENSI = 1` y `PP03J = 2`, ponderados / PEA ponderada × 100 | porcentaje |
| `ingreso_promedio_observado` | decimal o nulo | Promedio simple de `P21 > 0` entre ocupados | pesos nominales |
| `ingreso_mediano_observado` | decimal o nulo | Mediana de `P21 > 0` entre ocupados | pesos nominales |
| `ingreso_promedio_ponderado_observado` | decimal o nulo | suma(`P21 × PONDIIO`) / suma(`PONDIIO`) con `P21 > 0` y `PONDIIO > 0` | pesos nominales |
| `n_ocupados_con_ingreso_valido` | entero | Ocupados de muestra con `P21 > 0` | personas de muestra |
| `n_ocupados_con_pondiio_valido` | entero | Ocupados con `P21 > 0` y `PONDIIO` válido y positivo | personas de muestra |
| `n_ocupados_sin_respuesta_ingreso` | entero | Ocupados de muestra con `P21 = -9` | personas de muestra |
| `tasa_no_respuesta_ingresos_ocupados` | decimal | casos `P21 = -9` / ocupados de muestra × 100 | porcentaje |
| `hogares_encuestados` | entero | Registros de hogar con `REALIZADA = 1` | hogares publicados |
| `tasa_no_respuesta_hogar` | decimal | Control interno vigente basado en `REALIZADA = 0`; requiere revisión antes de interpretarse como no respuesta | control interno |
| `fecha_procesamiento` | texto | Fecha y hora de cálculo | fecha-hora |
| `fuente` | texto | Identificación del origen | texto |

`proporcion_inactiva_total` es un indicador complementario. Incluye por complemento a toda la población fuera de la PEA y no debe confundirse con `tasa_inactividad_10_mas`. Las tasas 14+ son específicas del universo de 14 años y más; las tasas 10+ se conservan como referencia histórica complementaria.

### Migración de nombres

| Nombre anterior | Nombre actual | Motivo |
|---|---|---|
| `tasa_actividad` | `tasa_actividad_10_mas` | El denominador anterior era población de 10 años y más |
| `tasa_empleo` | `tasa_empleo_10_mas` | El denominador anterior era población de 10 años y más |
| `tasa_inactividad` | `tasa_inactividad_10_mas` | El denominador anterior era población de 10 años y más |

## Calidad de datos

`calidad_datos_SDE_<periodo>.csv` informa por variable: `columna`, `nulos`, `codigo_-9_no_resp`, `codigo_-8`, `codigo_-7`, `validos` y `variable_disponible`. Cuando una variable no existe, sus conteos permanecen nulos. No se reemplazan por cero.

`calidad_snapshot_SDE.csv` contiene controles lógicos agregados cuando el portal funciona sin microdatos: población positiva, tasas en rango, complementariedad, duplicados y disponibilidad de informalidad. No reemplaza los conteos detallados del ETL.

## Estado de períodos

`estado_periodos.csv` contiene `periodo`, `fecha_esperada`, `fecha_deteccion`, `fecha_procesamiento_estado`, `intentos`, `estado`, `mensaje` y `ultima_actualizacion`.

Estados: `PENDIENTE`, `DESCARGADO`, `PROCESADO`, `EN_REVISION`, `VALIDADO`, `FALLIDO` y `PUBLICADO`.

## Metadatos

Todo CSV se acompaña por un archivo homónimo `.meta.json`. Incluye nombre, descripción, clasificación, fuente, organismo productor, URL, aglomerado, período, fecha, versión, dimensiones, variables, definiciones, tipos, unidades, fórmulas, filtros, ponderador, nulos, códigos especiales, advertencias, indicador de ingresos nominales, estado, última ejecución exitosa, archivo de origen, identificador de ejecución y SHA-256.

## Reglas de faltantes y alcance

- No se imputan faltantes.
- No se reemplazan faltantes por cero.
- En `2023T1`, `2023T2` y `2023T3`, la variable necesaria para estimar informalidad no está disponible. Por ese motivo, `tasa_informalidad` se presenta como no disponible y no se realiza imputación ni se reemplazan faltantes por cero.
- Los ingresos son nominales y requieren deflactación para comparaciones reales.
- El Aglomerado 18 no permite separar Santiago Capital de La Banda.
- El control interno `tasa_no_respuesta_hogar` utiliza actualmente `REALIZADA = 0`. Debe revisarse antes de interpretarlo como no respuesta, porque la codificación de diseño utilizada por el proyecto identifica 1=realizada y 2=no realizada.

## Salida `analisis_segmentado_SDE_AAAATn.csv` — V3.5

| Campo | Descripción |
|---|---|
| `periodo` | Trimestre en formato `AAAATn`. |
| `dimension` | Sexo, Edad, Nivel educativo, **Edad × Nivel educativo** o Decil de ingreso. |
| `categoria` | Categoría analizada dentro de la dimensión. |
| `universo` | Universo usado para el cálculo del segmento. |
| `n_muestra` | Registros observados de la muestra en el segmento. |
| `poblacion_expandida` | Población expandida mediante `PONDERA` para dimensiones laborales; en deciles de ingreso se utiliza `PONDIIO`. |
| `tasa_actividad` | PEA expandida / población expandida del segmento. |
| `tasa_empleo` | Ocupados expandidos / población expandida del segmento. |
| `tasa_desocupacion` | Desocupados expandidos / PEA expandida del segmento. |
| `tasa_informalidad` | Informales / ocupados con `EMPLEO` válido en el segmento. |
| `ingreso_promedio_ponderado_ocupados` | Promedio ponderado de `P21` entre ocupados con ingreso positivo, usando `PONDIIO`. |

Para la dimensión de deciles se utilizan `ADECOCUR` y `PONDIIO` cuando están disponibles. En esos registros las tasas laborales se dejan vacías porque la salida se centra en la distribución del ingreso de la ocupación principal.


## Indicadores de horas e intensidad — V3.5

La V3.5.0 incorpora un bloque derivado de `PP3E_TOT`, `PP3F_TOT` e `INTENSI`.

Reglas metodológicas:

- horas semanales totales = `PP3E_TOT + PP3F_TOT`;
- promedio semanal ponderado entre ocupados con horas válidas;
- mediana semanal ponderada;
- sobreocupación: `INTENSI = 3`, asociada a jornadas superiores a 45 horas semanales;
- tasa de sobreocupación calculada sobre la PEA.

Los nombres exactos de las columnas generadas por una corrida deben consultarse en `historico_SDE.csv` y en su archivo `.meta.json`, que constituyen la referencia de esquema de cada snapshot publicado. Esta sección documenta la definición metodológica y evita fijar nombres si cambian de manera explícita en una futura migración.

## Tamaño muestral en Edad × Nivel educativo

La V3.5.0 conserva `n_muestra` y `poblacion_expandida` para cada combinación.

Ayudas de lectura del portal:

- `n < 10`: muestra muy reducida; se mantiene visible, pero se excluye de máximos y mínimos automáticos;
- `10–29`: muestra reducida;
- `n >= 30`: base muestral más amplia.

Estos umbrales son ayudas operativas de lectura y **no constituyen reglas oficiales de precisión estadística del INDEC**.
