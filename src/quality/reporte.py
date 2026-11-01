"""Generación del reporte consolidado de calidad de las fuentes plata."""
from collections import defaultdict
from collections.abc import Mapping, Sequence

from src import config


def escribir_reporte_calidad(metricas: Sequence[Mapping[str, object]]) -> None:
    por_fuente: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for metrica in metricas:
        fuente = str(metrica.get("fuente", "EnerAndes"))
        por_fuente[fuente].append(metrica)

    resumen = []
    for fuente, filas in sorted(por_fuente.items()):
        entrada = sum(
            int(fila["antes"])
            for fila in filas
            if fila["problema"] in {"Registros en la fuente", "Filas de bronce recibidas"}
        )
        salida = sum(
            int(fila["despues"])
            for fila in filas
            if fila["problema"] in {"Filas válidas", "Filas limpias"}
        )
        cuarentena = sum(
            int(fila["despues"])
            for fila in filas
            if fila["problema"] in {
                "Filas inválidas enviadas a cuarentena",
                "Filas enviadas a cuarentena",
            }
        )
        resumen.append(
            f"| {fuente} | {entrada:,} | {salida:,} | {cuarentena:,} |"
        )

    lineas = [
        "# Reporte de calidad de la capa plata",
        "",
        "Las métricas se generan al ejecutar `python -m src.transformar`. "
        "Cada regla muestra el conteo antes y después; los datos no corregibles "
        "se conservan en su archivo de cuarentena.",
        "",
        "| Fuente/tabla | Filas recibidas | Filas plata | Filas en cuarentena |",
        "|---|---:|---:|---:|",
        *resumen,
        "",
    ]

    for fuente, filas in sorted(por_fuente.items()):
        lineas.extend([
            f"## {fuente}",
            "",
            "| Año | Problema de calidad | Regla aplicada | Antes | Después |",
            "|---:|---|---|---:|---:|",
        ])
        for fila in filas:
            anio = fila.get("anio", "—")
            regla = fila.get("regla aplicada", "—")
            lineas.append(
                f"| {anio} | {fila['problema']} | {regla} "
                f"| {int(fila['antes']):,} | {int(fila['despues']):,} |"
            )
        lineas.append("")

    config.DIR_DOCS.mkdir(parents=True, exist_ok=True)
    (config.DIR_DOCS / "reporte_calidad.md").write_text(
        "\n".join(lineas),
        encoding="utf-8",
    )
