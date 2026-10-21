from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from analisis_segmentado import generar_analisis_segmentado


DIR_DATOS = RAIZ / "data"
DIR_RESULTADOS = RAIZ / "results"
AGLOMERADO_OBJETIVO = 18


def extraer_periodo(nombre: str) -> tuple[int, int] | None:
    """
    Extrae año y trimestre desde nombres como:
    usu_individual_T425.txt -> (2025, 4)
    """
    coincidencia = re.search(r"T([1-4])(\d{2})", nombre, flags=re.IGNORECASE)

    if coincidencia is None:
        return None

    trimestre = int(coincidencia.group(1))
    anio = 2000 + int(coincidencia.group(2))

    return anio, trimestre


def main() -> None:
    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)

    archivos = sorted(
        DIR_DATOS.rglob("usu_individual_T*.txt")
    )

    if not archivos:
        raise FileNotFoundError(
            "No se encontraron microdatos individuales EPH en data/."
        )

    generados = []

    for archivo in archivos:
        periodo = extraer_periodo(archivo.name)

        if periodo is None:
            continue

        anio, trimestre = periodo

        # La V3.5 trabaja con el histórico 2023T1-2026T1.
        if not (
            (2023 <= anio <= 2025)
            or (anio == 2026 and trimestre == 1)
        ):
            continue

        print(f"Procesando {anio}T{trimestre}: {archivo}")

        datos = pd.read_csv(
            archivo,
            sep=";",
            low_memory=False,
        )

        if "AGLOMERADO" not in datos.columns:
            print("  OMITIDO: no contiene AGLOMERADO")
            continue

        datos["AGLOMERADO"] = pd.to_numeric(
            datos["AGLOMERADO"],
            errors="coerce",
        )

        sde = datos[
            datos["AGLOMERADO"] == AGLOMERADO_OBJETIVO
        ].copy()

        resultado = generar_analisis_segmentado(
            sde,
            anio,
            trimestre,
        )

        salida = (
            DIR_RESULTADOS
            / f"analisis_segmentado_SDE_{anio}T{trimestre}.csv"
        )

        resultado.to_csv(
            salida,
            index=False,
            encoding="utf-8-sig",
        )

        n_cruces = int(
            (
                resultado["dimension"]
                == "Edad × Nivel educativo"
            ).sum()
        )

        print(
            f"  OK -> {salida.name} "
            f"({len(resultado)} filas; "
            f"{n_cruces} cruces Edad × Educación)"
        )

        generados.append(f"{anio}T{trimestre}")

    print()
    print("===============================================")
    print("ANÁLISIS SEGMENTADOS GENERADOS")
    print("===============================================")
    print("Períodos:", len(generados))
    print(", ".join(generados))


if __name__ == "__main__":
    main()