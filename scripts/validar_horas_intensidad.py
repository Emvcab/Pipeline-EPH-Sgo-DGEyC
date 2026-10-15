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


def localizar_base(periodo: str) -> Path:
    anio = int(periodo[:4])
    trimestre = int(periodo[-1])

    carpeta = RAIZ / "data" / f"t{trimestre}_{anio}"

    archivos = [
        ruta
        for ruta in carpeta.rglob("*.txt")
        if "individual" in ruta.name.lower()
    ]

    if not archivos:
        raise FileNotFoundError(
            f"No se encontró base individual para {periodo}"
        )

    return archivos[0]


def main() -> None:
    filas = []
    extremos = []

    for periodo in PERIODOS:
        ruta = localizar_base(periodo)

        df = leer_archivo_eph(ruta)

        if df is None:
            raise RuntimeError(
                f"No se pudo leer {periodo}"
            )

        aglomerado = pd.to_numeric(
            df["AGLOMERADO"],
            errors="coerce",
        )

        estado = pd.to_numeric(
            df["ESTADO"],
            errors="coerce",
        )

        ocupados = df[
            aglomerado.eq(18)
            & estado.eq(1)
        ].copy()

        pp3e = pd.to_numeric(
            ocupados["PP3E_TOT"],
            errors="coerce",
        )

        pp3f = pd.to_numeric(
            ocupados["PP3F_TOT"],
            errors="coerce",
        )

        intensi = pd.to_numeric(
            ocupados["INTENSI"],
            errors="coerce",
        )

        horas = pp3e + pp3f

        filas.append(
            {
                "periodo": periodo,
                "n_ocupados": len(ocupados),

                # INTENSI = 1
                "i1_total":
                    int((intensi == 1).sum()),

                "i1_horas_menor35":
                    int(
                        (
                            (intensi == 1)
                            & (horas < 35)
                        ).sum()
                    ),

                "i1_horas_35omas":
                    int(
                        (
                            (intensi == 1)
                            & (horas >= 35)
                        ).sum()
                    ),

                # INTENSI = 2
                "i2_total":
                    int((intensi == 2).sum()),

                "i2_horas_menor35":
                    int(
                        (
                            (intensi == 2)
                            & (horas < 35)
                        ).sum()
                    ),

                "i2_horas_35a45":
                    int(
                        (
                            (intensi == 2)
                            & horas.between(
                                35,
                                45,
                                inclusive="both",
                            )
                        ).sum()
                    ),

                "i2_horas_mayor45":
                    int(
                        (
                            (intensi == 2)
                            & (horas > 45)
                        ).sum()
                    ),

                # INTENSI = 3
                "i3_total":
                    int((intensi == 3).sum()),

                "i3_horas_mayor45":
                    int(
                        (
                            (intensi == 3)
                            & (horas > 45)
                        ).sum()
                    ),

                "i3_horas_45omenos":
                    int(
                        (
                            (intensi == 3)
                            & (horas <= 45)
                        ).sum()
                    ),

                # INTENSI = 4
                "i4_total":
                    int((intensi == 4).sum()),

                "i4_horas_cero":
                    int(
                        (
                            (intensi == 4)
                            & (horas == 0)
                        ).sum()
                    ),

                "i4_horas_mayor0":
                    int(
                        (
                            (intensi == 4)
                            & (horas > 0)
                        ).sum()
                    ),

                "horas_min":
                    float(horas.min()),

                "horas_max":
                    float(horas.max()),

                "horas_mayor168":
                    int((horas > 168).sum()),
            }
        )

        # Casos extremos para revisión
        mascara_extremos = horas >= 90

        if mascara_extremos.any():
            vista = ocupados.loc[
                mascara_extremos,
                [
                    "ESTADO",
                    "PONDERA",
                    "PP3E_TOT",
                    "PP3F_TOT",
                    "INTENSI",
                ],
            ].copy()

            vista["periodo"] = periodo

            vista["horas_totales"] = (
                pd.to_numeric(
                    vista["PP3E_TOT"],
                    errors="coerce",
                )
                + pd.to_numeric(
                    vista["PP3F_TOT"],
                    errors="coerce",
                )
            )

            extremos.append(vista)

    resultado = pd.DataFrame(filas)

    print()
    print("=" * 135)
    print(
        "VALIDACION HORAS TOTALES VS INTENSI"
    )
    print("=" * 135)
    print()

    print(
        resultado.to_string(
            index=False
        )
    )

    print()
    print("=" * 135)
    print("COMPROBACION INTENSI = 2")
    print("=" * 135)

    comprobacion_i2 = resultado[
        [
            "periodo",
            "i2_total",
            "i2_horas_menor35",
            "i2_horas_35a45",
            "i2_horas_mayor45",
        ]
    ]

    print(
        comprobacion_i2.to_string(
            index=False
        )
    )

    print()
    print("=" * 135)
    print("CASOS CON 90 HORAS O MAS")
    print("=" * 135)

    if extremos:
        casos_extremos = pd.concat(
            extremos,
            ignore_index=True,
        )

        print(
            casos_extremos.to_string(
                index=False
            )
        )
    else:
        casos_extremos = pd.DataFrame()

        print("No se encontraron casos.")

    salida = (
        RAIZ
        / "results"
        / "validacion_horas_intensidad.csv"
    )

    resultado.to_csv(
        salida,
        index=False,
        encoding="utf-8-sig",
    )

    if not casos_extremos.empty:
        casos_extremos.to_csv(
            RAIZ
            / "results"
            / "casos_extremos_horas.csv",
            index=False,
            encoding="utf-8-sig",
        )

    print()
    print(f"Salida: {salida}")

    print()
    print("=" * 135)
    print("RESUMEN AUTOMATICO")
    print("=" * 135)

    total_i1_inconsistente = int(
        resultado["i1_horas_35omas"].sum()
    )

    total_i2_mayor45 = int(
        resultado["i2_horas_mayor45"].sum()
    )

    total_i3_inconsistente = int(
        resultado["i3_horas_45omenos"].sum()
    )

    total_i4_inconsistente = int(
        resultado["i4_horas_mayor0"].sum()
    )

    total_mayor168 = int(
        resultado["horas_mayor168"].sum()
    )

    print(
        f"INTENSI=1 con 35 horas o más : "
        f"{total_i1_inconsistente}"
    )

    print(
        f"INTENSI=2 con más de 45 horas: "
        f"{total_i2_mayor45}"
    )

    print(
        f"INTENSI=3 con 45 horas o menos: "
        f"{total_i3_inconsistente}"
    )

    print(
        f"INTENSI=4 con horas > 0       : "
        f"{total_i4_inconsistente}"
    )

    print(
        f"Horas totales > 168           : "
        f"{total_mayor168}"
    )


if __name__ == "__main__":
    main()