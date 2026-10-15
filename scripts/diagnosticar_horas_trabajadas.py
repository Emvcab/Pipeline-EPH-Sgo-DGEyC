from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.pipeline import leer_archivo_eph


PERIODOS = [
    "2023T1",
    "2023T2",
    "2023T3",
    "2023T4",
    "2024T1",
    "2024T2",
    "2024T3",
    "2024T4",
    "2025T1",
    "2025T2",
    "2025T3",
    "2025T4",
    "2026T1",
]

VARIABLES = [
    "ESTADO",
    "AGLOMERADO",
    "PONDERA",
    "PP3E_TOT",
    "PP3F_TOT",
    "INTENSI",
]


def localizar_base_individual(periodo: str) -> Path:
    anio = int(periodo[:4])
    trimestre = int(periodo[-1])

    carpeta = RAIZ / "data" / f"t{trimestre}_{anio}"

    if not carpeta.exists():
        raise FileNotFoundError(
            f"No existe la carpeta para {periodo}: {carpeta}"
        )

    archivos = [
        ruta
        for ruta in carpeta.rglob("*.txt")
        if "individual" in ruta.name.lower()
    ]

    if not archivos:
        raise FileNotFoundError(
            f"No se encontró la base individual para {periodo}"
        )

    return archivos[0]


def resumen_variable(
    serie: pd.Series,
) -> dict:
    numerica = pd.to_numeric(
        serie,
        errors="coerce",
    )

    validos = numerica.dropna()

    return {
        "n_no_nulos": int(validos.shape[0]),
        "n_nulos": int(numerica.isna().sum()),
        "minimo": (
            float(validos.min())
            if not validos.empty
            else None
        ),
        "maximo": (
            float(validos.max())
            if not validos.empty
            else None
        ),
        "n_cero": int((numerica == 0).sum()),
        "n_negativos": int((numerica < 0).sum()),
        "n_mayor_168": int((numerica > 168).sum()),
    }


def main() -> None:
    filas_resumen = []
    filas_valores = []

    print()
    print("=" * 90)
    print(
        "DIAGNOSTICO V3.5 - "
        "HORAS TRABAJADAS E INTENSIDAD"
    )
    print("=" * 90)

    for periodo in PERIODOS:
        print()
        print(f"Procesando {periodo}...")

        ruta = localizar_base_individual(
            periodo
        )

        df = leer_archivo_eph(ruta)

        if df is None:
            raise RuntimeError(
                f"No se pudo leer {periodo}"
            )

        faltantes = [
            variable
            for variable in VARIABLES
            if variable not in df.columns
        ]

        if faltantes:
            raise ValueError(
                f"{periodo}: faltan variables: "
                + ", ".join(faltantes)
            )

        aglomerado = pd.to_numeric(
            df["AGLOMERADO"],
            errors="coerce",
        )

        estado = pd.to_numeric(
            df["ESTADO"],
            errors="coerce",
        )

        sde = df[
            aglomerado.eq(18)
        ].copy()

        estado_sde = pd.to_numeric(
            sde["ESTADO"],
            errors="coerce",
        )

        ocupados = sde[
            estado_sde.eq(1)
        ].copy()

        if ocupados.empty:
            raise RuntimeError(
                f"{periodo}: no hay ocupados "
                "en el Aglomerado 18"
            )

        e = pd.to_numeric(
            ocupados["PP3E_TOT"],
            errors="coerce",
        )

        f = pd.to_numeric(
            ocupados["PP3F_TOT"],
            errors="coerce",
        )

        intensi = pd.to_numeric(
            ocupados["INTENSI"],
            errors="coerce",
        )

        peso = pd.to_numeric(
            ocupados["PONDERA"],
            errors="coerce",
        )

        resumen_e = resumen_variable(
            ocupados["PP3E_TOT"]
        )

        resumen_f = resumen_variable(
            ocupados["PP3F_TOT"]
        )

        # No se usa todavía como indicador.
        # Es únicamente un diagnóstico para observar
        # cómo se comportan las dos variables juntas.
        ambas_informadas = (
            e.notna()
            & f.notna()
        )

        horas_suma_diagnostica = (
            e + f
        ).where(
            ambas_informadas
        )

        filas_resumen.append(
            {
                "periodo": periodo,
                "n_personas_aglomerado": len(sde),
                "n_ocupados": len(ocupados),

                "pp3e_no_nulos":
                    resumen_e["n_no_nulos"],
                "pp3e_nulos":
                    resumen_e["n_nulos"],
                "pp3e_ceros":
                    resumen_e["n_cero"],
                "pp3e_min":
                    resumen_e["minimo"],
                "pp3e_max":
                    resumen_e["maximo"],
                "pp3e_negativos":
                    resumen_e["n_negativos"],
                "pp3e_mayor_168":
                    resumen_e["n_mayor_168"],

                "pp3f_no_nulos":
                    resumen_f["n_no_nulos"],
                "pp3f_nulos":
                    resumen_f["n_nulos"],
                "pp3f_ceros":
                    resumen_f["n_cero"],
                "pp3f_min":
                    resumen_f["minimo"],
                "pp3f_max":
                    resumen_f["maximo"],
                "pp3f_negativos":
                    resumen_f["n_negativos"],
                "pp3f_mayor_168":
                    resumen_f["n_mayor_168"],

                "ambas_horas_informadas":
                    int(ambas_informadas.sum()),

                "suma_diagnostica_min":
                    (
                        float(
                            horas_suma_diagnostica.min()
                        )
                        if horas_suma_diagnostica.notna().any()
                        else None
                    ),

                "suma_diagnostica_max":
                    (
                        float(
                            horas_suma_diagnostica.max()
                        )
                        if horas_suma_diagnostica.notna().any()
                        else None
                    ),

                "intensi_1":
                    int((intensi == 1).sum()),
                "intensi_2":
                    int((intensi == 2).sum()),
                "intensi_3":
                    int((intensi == 3).sum()),
                "intensi_4":
                    int((intensi == 4).sum()),
                "intensi_9":
                    int((intensi == 9).sum()),
                "intensi_nulos":
                    int(intensi.isna().sum()),

                "pondera_validos":
                    int(
                        (
                            peso.notna()
                            & peso.gt(0)
                        ).sum()
                    ),
            }
        )

        for variable in [
            "PP3E_TOT",
            "PP3F_TOT",
            "INTENSI",
        ]:
            serie = pd.to_numeric(
                ocupados[variable],
                errors="coerce",
            )

            conteos = (
                serie.value_counts(
                    dropna=False
                )
                .sort_index()
            )

            for valor, cantidad in conteos.items():
                filas_valores.append(
                    {
                        "periodo": periodo,
                        "variable": variable,
                        "valor": (
                            "NaN"
                            if pd.isna(valor)
                            else valor
                        ),
                        "cantidad": int(
                            cantidad
                        ),
                    }
                )

    resumen = pd.DataFrame(
        filas_resumen
    )

    valores = pd.DataFrame(
        filas_valores
    )

    salida_resumen = (
        RAIZ
        / "results"
        / "diagnostico_horas_trabajadas.csv"
    )

    salida_valores = (
        RAIZ
        / "results"
        / "diagnostico_horas_valores.csv"
    )

    salida_resumen.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resumen.to_csv(
        salida_resumen,
        index=False,
        encoding="utf-8-sig",
    )

    valores.to_csv(
        salida_valores,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("=" * 90)
    print("RESUMEN DE LOS 13 PERIODOS")
    print("=" * 90)

    columnas_mostrar = [
        "periodo",
        "n_ocupados",
        "pp3e_nulos",
        "pp3e_ceros",
        "pp3e_min",
        "pp3e_max",
        "pp3f_nulos",
        "pp3f_ceros",
        "pp3f_min",
        "pp3f_max",
        "intensi_1",
        "intensi_2",
        "intensi_3",
        "intensi_4",
        "intensi_9",
        "intensi_nulos",
    ]

    print(
        resumen[
            columnas_mostrar
        ].to_string(
            index=False
        )
    )

    print()
    print(
        f"Resumen guardado en: "
        f"{salida_resumen}"
    )

    print(
        f"Distribuciones guardadas en: "
        f"{salida_valores}"
    )

    print()
    print(
        "IMPORTANTE: la suma PP3E_TOT + PP3F_TOT "
        "mostrada aquí es sólo diagnóstica. "
        "Todavía no se utiliza como indicador."
    )


if __name__ == "__main__":
    main()