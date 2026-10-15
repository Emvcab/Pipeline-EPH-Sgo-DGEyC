# Corrección a partir de devolución docente

## Motivo

Durante la revisión del proyecto se señalaron dos aspectos de coherencia técnica y de documentación que debían fortalecerse antes del cierre V3.4.0.

### 1. Entorno de ejecución

La documentación y el EDA mezclaban el flujo real del proyecto con bloques orientados a Google Colab. Esa mezcla podía dar a entender que Colab era el entorno operativo del sistema y que las librerías se instalaban desde el propio código.

**Criterio corregido:**

- el pipeline, el monitor, los tests, los scripts auxiliares y Streamlit se ejecutan con **Python local** desde la raíz del repositorio;
- las dependencias se instalan previamente con `python -m pip install -r requirements.txt`;
- ningún script instala paquetes durante su ejecución;
- `notebooks/EDA_EPH_SDE.ipynb` se conserva como recurso demostrativo/exploratorio que consume un histórico agregado ya generado;
- si el notebook se muestra en Colab, su uso es únicamente demostrativo y no reemplaza al ETL.

## 2. Evolución del proyecto

La descripción histórica indicaba qué se había agregado, pero en algunos hitos no explicaba con suficiente precisión **cómo se hizo, por qué se necesitó y para qué mejoró el sistema**.

Se revisaron las descripciones de los hitos principales para hacer explícitas las decisiones técnicas:

- **V1.0:** se explica el flujo ETL por período: parametrización de año/trimestre, descarga y extracción del ZIP oficial, lectura de microdatos nacionales, filtro `AGLOMERADO == 18`, cálculo y acumulación del histórico.
- **V1.5:** se explica que la lectura robusta prueba combinaciones conocidas de separador/codificación y que los controles de calidad y logs se agregaron para detectar fallas antes de interpretar resultados y dejar evidencia de cada corrida.
- **V2.0:** se aclara que la reducción de 1.434 a 411 líneas fue consecuencia de separar responsabilidades, eliminar lógica repetida y tareas de uso único, centralizar configuración y hacer el código más mantenible y comprobable; no fue un objetivo de reducción de líneas por sí mismo.

## Archivos corregidos

- `scripts/eda_eph_sde.py`
- `notebooks/EDA_EPH_SDE.ipynb`
- `README.md`
- `CHANGELOG.md`
- `docs/MANUAL_TECNICO_PIPELINE.md`
- `docs/ARQUITECTURA.md`
- `docs/Manual_Pipeline_EPH.docx`
- `docs/Roadmap_Proximos_Pasos.docx`
- `docs/REGISTRO_CAMBIOS_V3_2_1.html`
- `docs/RELEASE_NOTES_V3_4_0.md`
- `docs/RELEASE_CHECKLIST_V3_4_0.md`

## Verificación posterior

- `python -m py_compile scripts/eda_eph_sde.py`: correcto.
- ejecución completa del notebook EDA sobre el snapshot agregado: correcta.
- `python -m pytest tests -q`: **97 passed**.

La corrección no modifica las fórmulas estadísticas ni la validación metodológica de la V3.4.0; ajusta la coherencia entre código, entorno real de ejecución y explicación técnica del proyecto.
