# Checklist de release V3.4.0

## Verificado

- [x] `PORTAL_VERSION = "3.4.0"`.
- [x] Tasas específicas 14+ implementadas y testeadas.
- [x] `P21` ponderado con `PONDIIO`, sin fallback silencioso a `PONDERA`.
- [x] `ADECOCUR` para deciles.
- [x] Validación externa: 27/27 concordancias (`2024T1`–`2026T1`).
- [x] Matriz metodológica y evidencia descargable.
- [x] PDF institucional integrado.
- [x] Suite actual: 97 tests aprobados.
- [x] Documentación de cierre actualizada.
- [x] Comparación territorial NOA/total declarada fuera de alcance.

## Pendiente antes de crear el tag final

- [ ] Reprocesar los períodos históricos con el código V3.4.0.
- [ ] Regenerar `data_snapshot/` con `python src/pipeline.py --publicar-snapshot`.
- [ ] Confirmar que `data_snapshot/historico_SDE.csv` contiene las columnas `tasa_actividad_14_mas`, `tasa_empleo_14_mas`, `tasa_desocupacion_14_mas` y `n_ocupados_con_pondiio_valido`.
- [ ] Confirmar que la metadata del histórico documenta `PONDIIO` para `ingreso_promedio_ponderado_observado`.
- [ ] Ejecutar nuevamente `python -m pytest tests -q` y obtener 97/97.
- [ ] Abrir Streamlit y revisar Calidad y auditoría, Ingresos y descarga PDF.
- [ ] Crear tag `v3.4.0` y GitHub Release.

## Comandos recomendados para regenerar

```powershell
python src/pipeline.py --anio 2023
python src/pipeline.py --anio 2024
python src/pipeline.py --anio 2025
python src/pipeline.py --anio 2026 --trimestre 1
python src/pipeline.py --publicar-snapshot
python -m pytest tests -q
```

Se evita `--todos` en este cierre para no intentar incorporar automáticamente un período posterior que todavía no deba formar parte del histórico de la release.
