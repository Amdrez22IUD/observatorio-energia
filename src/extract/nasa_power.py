"""Fuente NASA POWER: variables meteorologicas y radiacion solar diaria."""
import pandas as pd

from src import config
from src.utils import guardar_bronce, http_json, log, ya_existe

NOMBRE = "nasa_power_clima_diario"


def aplanar(respuesta: dict) -> list[dict]:
    """Pasa las series de parametros indexadas por fecha a filas diarias."""
    parametros = respuesta.get("properties", {}).get("parameter", {})
    faltantes = set(config.NASA_POWER_PARAMETROS) - set(parametros)
    if faltantes:
        raise ValueError(f"NASA POWER no devolvio los parametros esperados: {sorted(faltantes)}")

    fechas = sorted({
        fecha
        for serie in parametros.values()
        for fecha in serie
    })
    return [
        {
            "fecha": fecha,
            **{
                nombre: parametros[codigo].get(fecha)
                for codigo, nombre in config.NASA_POWER_PARAMETROS.items()
            },
        }
        for fecha in fechas
    ]


def extraer(forzar: bool = False) -> None:
    """Descarga el clima y la radiacion diaria del punto configurado en Antioquia."""
    log("NASA POWER - clima y radiacion solar")
    if ya_existe(NOMBRE, forzar):
        return

    parametros = {
        "parameters": ",".join(config.NASA_POWER_PARAMETROS),
        "community": config.NASA_POWER_COMUNIDAD,
        "longitude": config.NASA_POWER_LONGITUD,
        "latitude": config.NASA_POWER_LATITUD,
        "start": config.FECHA_INICIO.strftime("%Y%m%d"),
        "end": config.FECHA_FIN.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }
    respuesta = http_json("GET", config.NASA_POWER_URL, params=parametros)
    filas = aplanar(respuesta)
    origen = (
        f"{config.NASA_POWER_URL} "
        f"lat={config.NASA_POWER_LATITUD}, lon={config.NASA_POWER_LONGITUD}"
    )
    guardar_bronce(
        pd.DataFrame(filas),
        NOMBRE,
        fuente="NASA POWER",
        origen=origen,
    )
    log(f"   {len(filas)} dias descargados")


if __name__ == "__main__":
    import sys

    extraer(forzar="--forzar" in sys.argv)
