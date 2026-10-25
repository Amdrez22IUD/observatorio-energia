"""Perfilamiento descriptivo reproducible de los archivos de data/sample/."""
import pandas as pd

from src import config

DIR_SAMPLE = config.RAIZ / "data" / "sample"
HORAS = [f"Hour{hora:02d}" for hora in range(1, 25)]


def generar_hallazgos() -> list[str]:
    """Calcula hallazgos descriptivos y limitados a las muestras versionadas."""
    precio = pd.read_csv(DIR_SAMPLE / "xm_precio_bolsa.csv")
    precio_horas = precio[HORAS].apply(pd.to_numeric, errors="coerce")
    precio_largo = precio_horas.stack()
    precio_maximo = precio_largo.idxmax()
    fecha_precio = precio.loc[precio_maximo[0], "Date"]
    hora_precio = int(precio_maximo[1][4:])

    demanda = pd.read_csv(DIR_SAMPLE / "xm_demanda.csv")
    demanda_horas = demanda[HORAS].apply(pd.to_numeric, errors="coerce")
    demanda_pico = demanda_horas.stack().idxmax()
    hora_demanda_media = demanda_horas.mean().idxmax()
    fecha_demanda = demanda.loc[demanda_pico[0], "Date"]
    valor_demanda_pico = demanda_horas.stack().max()

    generacion = pd.read_csv(DIR_SAMPLE / "xm_generacion_recurso.csv")
    generacion_horas = generacion[HORAS].apply(pd.to_numeric, errors="coerce")
    promedio_por_recurso = generacion_horas.mean(axis=1)
    recurso_maximo = promedio_por_recurso.idxmax()

    aportes = pd.read_csv(DIR_SAMPLE / "xm_aportes_energia.csv")
    valores_aportes = pd.to_numeric(aportes["Value"], errors="coerce")
    aporte_maximo = valores_aportes.idxmax()

    embalses = pd.read_csv(DIR_SAMPLE / "xm_embalses.csv")
    embalses = embalses.sort_values("Date")
    nivel_inicio = float(embalses.iloc[0]["Value"]) * 100
    nivel_fin = float(embalses.iloc[-1]["Value"]) * 100

    recursos = pd.read_csv(DIR_SAMPLE / "xm_listado_recursos.csv")
    tipos_recursos = recursos["Type"].value_counts()

    precipitacion = pd.read_csv(DIR_SAMPLE / "ideam_precipitacion_diaria.csv")
    valores_precipitacion = pd.to_numeric(precipitacion["precipitacion_mm"], errors="coerce")
    fecha_precipitacion = precipitacion.iloc[0]["fecha"][:10]

    temperatura = pd.read_csv(DIR_SAMPLE / "ideam_temperatura_diaria.csv")
    promedios_temperatura = pd.to_numeric(
        temperatura["temperatura_promedio_c"],
        errors="coerce",
    )

    nasa = pd.read_csv(DIR_SAMPLE / "nasa_power_clima_diario.csv")
    nasa_temperatura = pd.to_numeric(nasa["temperatura_2m_c"], errors="coerce")
    nasa_lluvia = pd.to_numeric(nasa["precipitacion_corregida_mm_dia"], errors="coerce")
    nasa_radiacion = pd.to_numeric(nasa["radiacion_solar_kwh_m2_dia"], errors="coerce")

    oni = pd.read_csv(DIR_SAMPLE / "noaa_oni.csv")
    anomalias = pd.to_numeric(oni["ANOM"], errors="coerce")

    return [
        (
            f"XM precio: media de {precio_largo.mean():.2f} COP/kWh; "
            f"maximo de {precio_largo.max():.2f} COP/kWh el {fecha_precio}, hora {hora_precio:02d}."
        ),
        (
            f"XM demanda: la hora con mayor promedio en la muestra es {hora_demanda_media[4:]}; "
            f"pico observado de {valor_demanda_pico:,.2f} el {fecha_demanda}."
        ),
        (
            f"XM generacion: {generacion['code'].nunique()} recursos muestreados; "
            f"su promedio horario por recurso va de {promedio_por_recurso.min():,.2f} "
            f"a {promedio_por_recurso.max():,.2f}."
        ),
        (
            f"XM aportes de energia: promedio diario de {valores_aportes.mean():,.2f}; "
            f"maximo de {valores_aportes.max():,.2f} el {aportes.loc[aporte_maximo, 'Date']}."
        ),
        (
            f"XM embalses: el nivel paso de {nivel_inicio:.2f}% a {nivel_fin:.2f}%, "
            f"un cambio de {nivel_fin - nivel_inicio:+.2f} puntos porcentuales."
        ),
        (
            f"XM listado de recursos: {recursos['Code'].nunique()} recursos en la muestra; "
            f"{int(tipos_recursos.get('HIDRAULICA', 0))} hidraulicos y "
            f"{int(tipos_recursos.get('TERMICA', 0))} termicos."
        ),
        (
            f"IDEAM precipitacion: {len(valores_precipitacion)} estaciones muestreadas "
            f"el {fecha_precipitacion}; promedio {valores_precipitacion.mean():.2f} mm, "
            f"rango {valores_precipitacion.min():.2f}-{valores_precipitacion.max():.2f} mm."
        ),
        (
            f"IDEAM temperatura: {len(promedios_temperatura)} estaciones; promedio de "
            f"temperatura media diaria {promedios_temperatura.mean():.2f} °C, "
            f"rango {promedios_temperatura.min():.2f}-{promedios_temperatura.max():.2f} °C."
        ),
        (
            f"NASA POWER: {len(nasa)} dias; promedios de temperatura {nasa_temperatura.mean():.2f} °C, "
            f"precipitacion {nasa_lluvia.mean():.2f} mm/dia y radiacion "
            f"{nasa_radiacion.mean():.2f} kWh/m²/dia."
        ),
        (
            f"NOAA ONI: {len(anomalias)} registros estacionales; anomalia de temperatura "
            f"superficial del mar entre {anomalias.min():.2f} y {anomalias.max():.2f} °C."
        ),
    ]


def main() -> None:
    print("Perfilamiento exploratorio de data/sample/ (no representa el universo completo)")
    for numero, hallazgo in enumerate(generar_hallazgos(), start=1):
        print(f"{numero}. {hallazgo}")


if __name__ == "__main__":
    main()
