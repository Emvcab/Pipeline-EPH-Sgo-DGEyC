import pandas as pd

from src.pipeline import calcular_presion_mercado_trabajo


def test_presion_mercado_trabajo_usa_pea_y_pondera():
    """
    PEA expandida = 200.

    Ocupados demandantes:
    20 + 30 = 50 -> 25%

    Subocupados:
    20 + 10 = 30 -> 15%

    Subocupados demandantes:
    20 -> 10%

    Subocupados no demandantes:
    10 -> 5%

    El inactivo de peso 500 no debe entrar en la PEA.
    """
    df = pd.DataFrame(
        {
            "ESTADO": [1, 1, 1, 1, 2, 3],
            "PONDERA": [20, 10, 30, 40, 100, 500],
            "INTENSI": [1, 1, 2, 2, 0, 0],
            "PP03J": [1, 2, 1, 2, 0, 0],
        }
    )

    r = calcular_presion_mercado_trabajo(df)

    assert r["pea_expandida_presion"] == 200
    assert r["ocupados_demandantes_expandidos"] == 50
    assert r["subocupados_expandidos"] == 30
    assert r["subocupados_demandantes_expandidos"] == 20
    assert r["subocupados_no_demandantes_expandidos"] == 10

    assert r["tasa_ocupados_demandantes"] == 25.0
    assert r["tasa_subocupacion"] == 15.0
    assert r["tasa_subocupacion_demandante"] == 10.0
    assert r["tasa_subocupacion_no_demandante"] == 5.0