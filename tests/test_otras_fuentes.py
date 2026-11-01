import pandas as pd

from src.quality.esquemas import (
    ESQUEMA_IDEAM_PRECIPITACION,
    ESQUEMA_NASA_POWER,
    ESQUEMA_NOAA_ONI,
    ESQUEMA_XM_PRECIO_BOLSA,
)
from src.silver.otras_fuentes import (
    fase_enso,
    limpiar_ideam,
    limpiar_nasa_power,
    limpiar_noaa,
    limpiar_xm_horario,
)


def _fila_xm(fecha: str = "2024-01-01") -> dict[str, object]:
    return {
        "Date": fecha,
        "Id": "Sistema",
        "code": "Sistema",
        **{
            f"Hour{hora:02d}": "" if hora == 2 else str(hora * 10)
            for hora in range(1, 25)
        },
    }


def test_xm_horario_convierte_24_columnas_en_filas_numericas():
    limpias, cuarentena, _ = limpiar_xm_horario(
        pd.DataFrame([_fila_xm()]),
        columna_valor="precio_bolsa",
    )

    assert len(limpias) == 24
    assert cuarentena.empty
    assert limpias["hora"].tolist() == list(range(1, 25))
    assert limpias.loc[0, "precio_bolsa"] == 10
    assert pd.isna(limpias.loc[1, "precio_bolsa"])
    ESQUEMA_XM_PRECIO_BOLSA.validate(limpias, lazy=True)


def test_xm_horario_conserva_filas_no_numericas_en_cuarentena():
    fila = _fila_xm()
    fila["Hour03"] = "sin dato"

    limpias, cuarentena, _ = limpiar_xm_horario(
        pd.DataFrame([fila]),
        columna_valor="precio_bolsa",
    )

    assert len(limpias) == 23
    assert len(cuarentena) == 1
    assert cuarentena.loc[0, "motivo_cuarentena"] == "valor horario no numérico"


def test_noaa_asigna_trimestres_al_mes_central_del_anio_indicado():
    bronce = pd.DataFrame({
        "SEAS": ["DJF", "JFM", "FMA", "NDJ"],
        "YR": ["2026"] * 4,
        "TOTAL": ["25.0"] * 4,
        "ANOM": ["0.5", "-0.5", "0.49", "-0.49"],
    })

    limpias, cuarentena, _ = limpiar_noaa(bronce)

    assert cuarentena.empty
    assert limpias["fecha"].dt.strftime("%Y-%m-%d").tolist() == [
        "2026-01-01", "2026-02-01", "2026-03-01", "2026-12-01",
    ]
    assert limpias["fase_enso"].tolist() == ["El Niño", "La Niña", "Neutral", "Neutral"]
    ESQUEMA_NOAA_ONI.validate(limpias, lazy=True)


def test_fase_enso_aplica_los_umbral_incluyendo_los_limites():
    assert fase_enso(0.5) == "El Niño"
    assert fase_enso(-0.5) == "La Niña"
    assert fase_enso(0.49) == "Neutral"


def test_ideam_convierte_tipos_y_conserva_municipio_de_estacion():
    bronce = pd.DataFrame([{
        "codigoestacion": "001234",
        "nombreestacion": "ESTACION UNO",
        "municipio": "MEDELLIN",
        "latitud": "6.25",
        "longitud": "-75.56",
        "fecha": "2025-01-02T00:00:00.000",
        "precipitacion_mm": "12.5",
        "n_obs": "4",
    }])

    limpias, cuarentena, _ = limpiar_ideam(
        bronce,
        {"precipitacion_mm": "precipitacion_mm"},
    )

    assert cuarentena.empty
    assert limpias.loc[0, "municipio"] == "Medellin"
    assert limpias.loc[0, "precipitacion_mm"] == 12.5
    assert limpias.loc[0, "fecha"] == pd.Timestamp("2025-01-02")
    ESQUEMA_IDEAM_PRECIPITACION.validate(limpias, lazy=True)


def test_nasa_power_trata_menos_999_como_dato_ausente():
    bronce = pd.DataFrame([{
        "fecha": "20260103",
        "temperatura_2m_c": 18.5,
        "precipitacion_corregida_mm_dia": 1.2,
        "radiacion_solar_kwh_m2_dia": -999.0,
    }])

    limpias, cuarentena, _ = limpiar_nasa_power(bronce)

    assert cuarentena.empty
    assert limpias.loc[0, "fecha"] == pd.Timestamp("2026-01-03")
    assert pd.isna(limpias.loc[0, "radiacion_solar_kwh_m2_dia"])
    ESQUEMA_NASA_POWER.validate(limpias, lazy=True)
