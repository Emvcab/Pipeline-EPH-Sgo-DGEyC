from __future__ import annotations

import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.pipeline import (
    calcular_presion_mercado_trabajo,
    leer_archivo_eph,
)


RUTA_REFERENCIA = (
    RAIZ / "docs" / "referencia_indec_presion_laboral.csv"
)

RUTA_SALIDA = (
    RAIZ / "results" / "validacion_presion_laboral_indec.csv"
)


INDICADORES = {
    "ocupados_demandantes": {
        "tasa": "tasa_ocupados_demandantes",
        "numerador": "ocupados_demandantes_expandidos",
    },
    "subocupacion": {
        "tasa": "tasa_subocupacion",
        "numerador": "subocupados_expandidos",
    },
    "subocupacion_demandante": {
        "tasa": "tasa_subocupacion_demandante",
        "numerador": "subocupados_demandantes_expandidos",
    },
    "subocupacion_no_demandante": {
        "tasa": "tasa_subocupacion_no_demandante",
        "numerador": "subocupados_no_demandantes_expandidos",
    },
}


def redondear_publicacion(valor: float) -> float:
    """
    Redondea a una cifra decimal con criterio ROUND_HALF_UP.
    """
    return float(
        Decimal(str(valor)).quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP,
        )
    )


def cargar_microdatos(periodo: str) -> pd.DataFrame:
    """
    Carga la base individual correspondiente a un período YYYYTx.
    """
    anio = int(periodo[:4])
    trimestre = int(periodo[-1])

    carpeta = RAIZ / "data" / f"t{trimestre}_{anio}"

    if not carpeta.exists():
        raise FileNotFoundError(
            f"No existe la carpeta de microdatos para "
            f"{periodo}: {carpeta}"
        )

    archivos = list(
        carpeta.rglob("*individual*.txt")
    )

    if not archivos:
        raise FileNotFoundError(
            f"No se encontró la base individual para {periodo}"
        )

    df = leer_archivo_eph(archivos[0])

    if df is None:
        raise RuntimeError(
            "No se pudo leer la base individual "
            f"correspondiente a {periodo}"
        )

    return df


def calcular_periodo(periodo: str) -> dict:
    """
    Calcula los indicadores de presión laboral
    para Santiago del Estero - La Banda.
    """
    df = cargar_microdatos(periodo)

    aglomerado = pd.to_numeric(
        df["AGLOMERADO"],
        errors="coerce",
    )

    sde = df[aglomerado == 18].copy()

    if sde.empty:
        raise RuntimeError(
            f"El Aglomerado 18 no está presente en {periodo}"
        )

    return calcular_presion_mercado_trabajo(sde)


def main() -> None:
    """
    Compara los indicadores calculados desde los microdatos
    contra los valores oficiales publicados por INDEC.

    La comparación a una cifra decimal se realiza desde
    los cocientes ponderados originales, evitando doble redondeo.
    """
    if not RUTA_REFERENCIA.exists():
        raise FileNotFoundError(
            f"No se encontró {RUTA_REFERENCIA}"
        )

    referencia = pd.read_csv(RUTA_REFERENCIA)

    columnas_requeridas = {
        "periodo",
        "ocupados_demandantes",
        "subocupacion",
        "subocupacion_demandante",
        "subocupacion_no_demandante",
    }

    faltantes = columnas_requeridas - set(
        referencia.columns
    )

    if faltantes:
        raise ValueError(
            "Faltan columnas en la referencia INDEC: "
            + ", ".join(sorted(faltantes))
        )

    filas = []

    for _, fila_ref in referencia.iterrows():
        periodo = str(fila_ref["periodo"]).strip()

        calculados = calcular_periodo(periodo)

        pea = float(
            calculados["pea_expandida_presion"]
        )

        if pea <= 0:
            raise RuntimeError(
                f"La PEA expandida no es válida en {periodo}"
            )

        for indicador_indec, claves in INDICADORES.items():

            numerador = float(
                calculados[claves["numerador"]]
            )

            # Tasa sin ningún redondeo previo.
            tasa_cruda = numerador / pea * 100

            # Se conserva también la tasa a 2 decimales
            # producida normalmente por el pipeline.
            tasa_pipeline = calculados[
                claves["tasa"]
            ]

            valor_indec = float(
                fila_ref[indicador_indec]
            )

            pipeline_1_decimal = (
                redondear_publicacion(tasa_cruda)
            )

            indec_1_decimal = (
                redondear_publicacion(valor_indec)
            )

            diferencia = round(
                tasa_cruda - valor_indec,
                4,
            )

            estado = (
                "OK"
                if pipeline_1_decimal
                == indec_1_decimal
                else "REVISAR"
            )

            filas.append(
                {
                    "periodo": periodo,
                    "indicador": claves["tasa"],
                    "pipeline": tasa_pipeline,
                    "pipeline_crudo": tasa_cruda,
                    "pipeline_1_decimal": pipeline_1_decimal,
                    "indec_publicado": indec_1_decimal,
                    "diferencia_pp": diferencia,
                    "estado": estado,
                }
            )

    comparacion = pd.DataFrame(filas)

    RUTA_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparacion.to_csv(
        RUTA_SALIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("=" * 95)
    print(
        "VALIDACION V3.5 - "
        "PRESION SOBRE EL MERCADO DE TRABAJO"
    )
    print("=" * 95)
    print()

    columnas_mostrar = [
        "periodo",
        "indicador",
        "pipeline",
        "pipeline_crudo",
        "pipeline_1_decimal",
        "indec_publicado",
        "diferencia_pp",
        "estado",
    ]

    print(
        comparacion[
            columnas_mostrar
        ].to_string(index=False)
    )

    total = len(comparacion)

    ok = int(
        (comparacion["estado"] == "OK").sum()
    )

    revisar = total - ok

    periodos = comparacion[
        "periodo"
    ].nunique()

    indicadores = comparacion[
        "indicador"
    ].nunique()

    print()
    print("=" * 95)
    print("RESUMEN")
    print("=" * 95)
    print(f"Comparaciones totales : {total}")
    print(f"Concordancias OK      : {ok}")
    print(f"Requieren revisión    : {revisar}")
    print(f"Períodos              : {periodos}")
    print(f"Indicadores           : {indicadores}")

    print()
    print(f"Salida: {RUTA_SALIDA}")

    if revisar > 0:
        print()
        print("COMPARACIONES A REVISAR")
        print("-" * 95)

        pendientes = comparacion[
            comparacion["estado"] != "OK"
        ]

        print(
            pendientes[
                columnas_mostrar
            ].to_string(index=False)
        )

        print()
        print("VALIDACION NO SUPERADA")

        raise SystemExit(1)

    print()
    print("VALIDACION SUPERADA")


if __name__ == "__main__":
    main()