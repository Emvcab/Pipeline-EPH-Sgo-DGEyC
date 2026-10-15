import pandas as pd

from src.pipeline import calcular_horas_e_intensidad


def test_calcular_horas_e_intensidad():
    df = pd.DataFrame(
        {
            "ESTADO": [1, 1, 1, 1, 2],
            "PONDERA": [2, 1, 1, 3, 3],
            "PP3E_TOT": [20, 40, 50, 0, 0],
            "PP3F_TOT": [0, 0, 0, 0, 0],
            "INTENSI": [1, 2, 3, 4, None],
        }
    )

    resultado = calcular_horas_e_intensidad(df)

    assert resultado["sobreocupados_expandidos"] == 1
    assert resultado["tasa_sobreocupacion_horaria"] == 10.0
    assert resultado["ocupados_que_trabajaron_expandidos"] == 4
    assert resultado["promedio_horas_semanales_ponderado"] == 32.5
    assert resultado["n_ocupados_horas_validas"] == 3