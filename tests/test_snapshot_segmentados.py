import pandas as pd

from src.pipeline import preparar_snapshot_desde_historico


def test_snapshot_preserva_analisis_segmentado_existente(tmp_path):
    """
    Verifica que al reconstruir data_snapshot no se eliminen
    los análisis segmentados ya publicados cuando results/
    no contiene nuevas versiones.
    """

    historico = pd.DataFrame(
        [
            {
                "anio": 2025,
                "trimestre": 4,
                "periodo": "2025T4",
                "aglomerado": 18,
                "n_personas_muestra": 1000,
                "n_hogares_muestra": 400,
                "poblacion_expandida_total": 1000,
                "poblacion_expandida_mayor10": 900,
                "pea_expandida": 500,
                "ocupados_expandidos": 450,
                "desocupados_expandidos": 50,
                "inactivos_expandidos": 400,
                "tasa_informalidad": 30.0,
                "fecha_procesamiento": "2026-01-01 00:00:00",
            }
        ]
    )

    ruta_historico = tmp_path / "historico_SDE.csv"
    historico.to_csv(ruta_historico, index=False)

    destino = tmp_path / "data_snapshot"
    destino.mkdir()

    results = tmp_path / "results"
    results.mkdir()

    archivo_segmentado = (
        destino / "analisis_segmentado_SDE_2025T4.csv"
    )

    archivo_segmentado.write_text(
        "periodo,dimension,categoria,valor\n"
        "2025T4,Sexo,Mujer,10.5\n",
        encoding="utf-8",
    )

    meta_segmentado = (
        destino / "analisis_segmentado_SDE_2025T4.meta.json"
    )

    meta_segmentado.write_text(
        '{"estado_validacion": "VALIDADO"}',
        encoding="utf-8",
    )

    contenido_original = archivo_segmentado.read_text(
        encoding="utf-8"
    )

    preparar_snapshot_desde_historico(
        ruta_historico=ruta_historico,
        destino=destino,
        validaciones_existentes=results,
    )

    assert archivo_segmentado.exists()

    assert meta_segmentado.exists()

    assert (
        archivo_segmentado.read_text(encoding="utf-8")
        == contenido_original
    )