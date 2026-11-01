"""Construye las capas plata y oro a partir de los Parquet de bronce existentes.

Uso:
    python -m src.transformar
"""
import subprocess
import sys
import time
from pathlib import Path

from src import config
from src.quality.reporte import escribir_reporte_calidad
from src.silver import enerandes, otras_fuentes
from src.utils import log

FUENTES_BRONCE = [
    *(f"enerandes_ventas_{anio}.parquet" for anio in range(2023, 2027)),
    "xm_precio_bolsa.parquet",
    "xm_demanda.parquet",
    "xm_generacion_recurso.parquet",
    "xm_embalses.parquet",
    "xm_aportes_energia.parquet",
    "xm_listado_recursos.parquet",
    "ideam_precipitacion_diaria.parquet",
    "ideam_temperatura_diaria.parquet",
    "noaa_oni.parquet",
    "nasa_power_clima_diario.parquet",
]


def _validar_bronce_disponible() -> None:
    faltantes = [
        nombre for nombre in FUENTES_BRONCE
        if not (config.DIR_BRONZE / nombre).is_file()
    ]
    if faltantes:
        lista = "\n".join(f"- {nombre}" for nombre in faltantes)
        raise FileNotFoundError(
            "Faltan archivos de la capa bronce necesarios para transformar:\n"
            f"{lista}\nEjecute primero `python -m src.pipeline`."
        )


def _ruta_dbt() -> Path:
    nombre = "dbt.exe" if sys.platform == "win32" else "dbt"
    ejecutable = Path(sys.executable).parent / nombre
    if not ejecutable.is_file():
        raise FileNotFoundError(
            f"No se encontró dbt en el entorno Python activo: {ejecutable}. "
            "Active .venv e instale requirements.txt."
        )
    return ejecutable


def main() -> None:
    inicio = time.time()
    _validar_bronce_disponible()
    log("Construcción de las capas plata y oro")
    metricas = enerandes.main()
    metricas.extend(otras_fuentes.main())
    escribir_reporte_calidad(metricas)
    log("Reporte consolidado en docs/reporte_calidad.md")

    comando = [
        str(_ruta_dbt()),
        "build",
        "--project-dir",
        "dbt",
        "--profiles-dir",
        "dbt",
    ]
    log("Ejecutando dbt build")
    subprocess.run(comando, check=True, cwd=config.RAIZ)
    log(f"Capas plata y oro listas en {time.time() - inicio:.0f} s")


if __name__ == "__main__":
    main()
