"""Exporta muestras publicas y genera el perfil tecnico de la capa bronce."""
from datetime import datetime

import pandas as pd

from src import config

DIR_SAMPLE = config.RAIZ / "data" / "sample"
RUTA_REPORTE = config.RAIZ / "docs" / "perfilamiento.md"
ARCHIVOS_ESPERADOS = (
    "xm_precio_bolsa",
    "xm_demanda",
    "xm_embalses",
    "xm_generacion_recurso",
    "xm_aportes_energia",
    "xm_listado_recursos",
    "ideam_precipitacion_diaria",
    "ideam_temperatura_diaria",
    "nasa_power_clima_diario",
    "noaa_oni",
    "enerandes_ventas_2023",
    "enerandes_ventas_2024",
    "enerandes_ventas_2025",
    "enerandes_ventas_2026",
)
def exportar_muestras() -> list[str]:
    """Guarda las primeras 200 filas de cada Parquet disponible."""
    DIR_SAMPLE.mkdir(parents=True, exist_ok=True)
    exportados = []
    for archivo in sorted(config.DIR_BRONZE.glob("*.parquet")):
        muestra = pd.read_parquet(archivo).head(200)
        muestra.to_csv(DIR_SAMPLE / f"{archivo.stem}.csv", index=False, encoding="utf-8")
        exportados.append(archivo.stem)
    return exportados


def _rangos_fecha(df: pd.DataFrame) -> str:
    rangos = []
    for columna in df.columns:
        nombre = columna.lower()
        if nombre not in {"date", "fecha", "yr", "year"}:
            continue
        valores = df[columna]
        if nombre in {"yr", "year"}:
            valores = pd.to_datetime(valores, format="%Y", errors="coerce")
        else:
            valores = pd.to_datetime(valores, errors="coerce")
        valores = valores.dropna()
        if not valores.empty:
            rangos.append(f"{columna}: {valores.min().date()} a {valores.max().date()}")
    return "; ".join(rangos) if rangos else "No identificable en las columnas"


def _tabla_archivo(nombre: str, df: pd.DataFrame) -> list[str]:
    lineas = [
        f"### `{nombre}.parquet`",
        "",
        f"- Filas: **{len(df):,}**",
        f"- Columnas: **{len(df.columns)}**",
        f"- Filas duplicadas completas: **{int(df.duplicated().sum()):,}**",
        f"- Rango de fechas: {_rangos_fecha(df)}",
        "",
        "| Columna | Tipo | Nulos | Nulos (%) |",
        "| --- | --- | ---: | ---: |",
    ]
    for columna in df.columns:
        nulos = int(df[columna].isna().sum())
        porcentaje = (100 * nulos / len(df)) if len(df) else 0
        lineas.append(
            f"| `{columna}` | `{df[columna].dtype}` | {nulos:,} | {porcentaje:.2f}% |"
        )
    lineas.append("")
    return lineas


def _hallazgos_calidad(datos: dict[str, pd.DataFrame]) -> list[str]:
    filas_perfiladas = sum(len(df) for df in datos.values())
    celdas_perfiladas = sum(df.size for df in datos.values())
    nulos = sum(int(df.isna().sum().sum()) for df in datos.values())
    duplicados = sum(int(df.duplicated().sum()) for df in datos.values())
    faltantes = sorted(set(ARCHIVOS_ESPERADOS) - set(datos))

    nasa = datos.get("nasa_power_clima_diario")
    marcadores_nasa = None
    if nasa is not None:
        numericas = nasa.select_dtypes(include="number")
        marcadores_nasa = int(numericas.eq(-999).sum().sum())

    archivos_horarios = [
        (nombre, df)
        for nombre, df in datos.items()
        if nombre in {"xm_precio_bolsa", "xm_demanda", "xm_generacion_recurso"}
    ]
    celdas_horarias = 0
    invalidas_horarias = 0
    for _, df in archivos_horarios:
        columnas_hora = [col for col in df.columns if col.startswith("Hour")]
        valores = df[columnas_hora].apply(pd.to_numeric, errors="coerce")
        celdas_horarias += int(valores.size)
        invalidas_horarias += int(valores.isna().sum().sum())

    rangos_fuera_de_inicio = []
    for nombre, df in datos.items():
        columna_fecha = next(
            (col for col in df.columns if col.lower() in {"date", "fecha"}),
            None,
        )
        if columna_fecha is None:
            continue
        fechas = pd.to_datetime(df[columna_fecha], errors="coerce").dropna()
        if fechas.empty:
            continue
        if nombre.startswith("ideam_"):
            fecha_esperada = config.IDEAM_FECHA_INICIO
        elif nombre.startswith(("xm_", "nasa_")):
            fecha_esperada = config.FECHA_INICIO
        else:
            continue
        if fechas.min().date() > fecha_esperada:
            rangos_fuera_de_inicio.append(
                f"{nombre}: inicia {fechas.min().date()}, se esperaba desde {fecha_esperada}"
            )

    return [
        (
            f"El perfil cubre {len(datos)} archivos presentes, "
            f"{filas_perfiladas:,} filas y {celdas_perfiladas:,} celdas."
        ),
        (
            f"Se encontraron {nulos:,} valores nulos explícitos "
            f"({(100 * nulos / celdas_perfiladas if celdas_perfiladas else 0):.4f}% "
            "de las celdas perfiladas)."
        ),
        (
            f"Se encontraron {duplicados:,} filas duplicadas completas "
            f"en los {filas_perfiladas:,} registros perfilados."
        ),
        (
            f"En las series horarias XM perfiladas hay {invalidas_horarias:,} valores "
            f"no numéricos/nulos entre {celdas_horarias:,} celdas horarias."
        ),
        (
            (
                f"NASA POWER contiene {marcadores_nasa:,} valores de relleno `-999`."
                if marcadores_nasa is not None
                else "NASA POWER no tiene Parquet local; el control del marcador `-999` no se ejecutó."
            )
        ),
        (
            f"Faltan localmente {len(faltantes)} archivos configurados "
            f"para perfilar: {', '.join(faltantes) if faltantes else 'ninguno'}."
        ),
        (
            "Archivos cuya fecha mínima no alcanza el inicio configurado: "
            f"{'; '.join(rangos_fuera_de_inicio) if rangos_fuera_de_inicio else 'ninguno'}."
        ),
    ]


def generar_reporte() -> str:
    """Genera docs/perfilamiento.md desde los Parquet locales."""
    datos = {
        archivo.stem: pd.read_parquet(archivo)
        for archivo in sorted(config.DIR_BRONZE.glob("*.parquet"))
    }
    RUTA_REPORTE.parent.mkdir(parents=True, exist_ok=True)
    lineas = [
        "# Perfilamiento de la capa bronce",
        "",
        f"Generado: {datetime.now().astimezone().isoformat(timespec='minutes')}.",
        "",
        "Este reporte describe los Parquet encontrados en `data/bronze/` "
        "en el momento de su generación. Vuelva a generarlo después de ejecutar "
        "`python -m src.pipeline` para reflejar la extracción completa.",
        "",
        "El archivo de EnerAndes usado en esta actividad es recreativo y educativo; "
        "se incluyen sus Parquet y muestras de hasta 200 filas.",
        "",
        "## Hallazgos de calidad",
        "",
    ]
    lineas.extend(
        f"{numero}. {hallazgo}"
        for numero, hallazgo in enumerate(_hallazgos_calidad(datos), start=1)
    )
    lineas.extend(["", "## Archivos presentes", ""])
    for nombre, df in datos.items():
        lineas.extend(_tabla_archivo(nombre, df))

    lineas.extend(["## Archivos esperados no encontrados", ""])
    ausentes = sorted(set(ARCHIVOS_ESPERADOS) - set(datos))
    if ausentes:
        lineas.extend(f"- `{nombre}.parquet`" for nombre in ausentes)
    else:
        lineas.append("Todos los archivos esperados están disponibles.")

    contenido = "\n".join(lineas) + "\n"
    RUTA_REPORTE.write_text(contenido, encoding="utf-8")
    return contenido


def main() -> None:
    muestras = exportar_muestras()
    generar_reporte()
    print(f"Muestras exportadas: {len(muestras)} (máximo 200 filas cada una).")
    print(f"Reporte generado: {RUTA_REPORTE}")
    print("Hallazgos documentados: 7.")


if __name__ == "__main__":
    main()
