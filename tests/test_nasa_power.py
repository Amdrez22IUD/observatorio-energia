import pytest

from src import config
from src.extract import nasa_power


def test_aplanar_convierte_series_diarias_en_filas():
    respuesta = {
        "properties": {
            "parameter": {
                "T2M": {"20240101": 18.29, "20240102": 19.0},
                "PRECTOTCORR": {"20240101": 1.28, "20240102": 0.28},
                "ALLSKY_SFC_SW_DWN": {"20240101": 4.9642, "20240102": 4.9922},
            },
        },
    }

    assert nasa_power.aplanar(respuesta) == [
        {
            "fecha": "20240101",
            "temperatura_2m_c": 18.29,
            "precipitacion_corregida_mm_dia": 1.28,
            "radiacion_solar_kwh_m2_dia": 4.9642,
        },
        {
            "fecha": "20240102",
            "temperatura_2m_c": 19.0,
            "precipitacion_corregida_mm_dia": 0.28,
            "radiacion_solar_kwh_m2_dia": 4.9922,
        },
    ]


def test_aplanar_falla_si_la_api_omite_un_parametro():
    respuesta = {"properties": {"parameter": {"T2M": {}}}}

    with pytest.raises(ValueError) as error:
        nasa_power.aplanar(respuesta)

    assert "ALLSKY_SFC_SW_DWN" in str(error.value)
    assert "PRECTOTCORR" in str(error.value)


def test_extraer_pide_rango_y_punto_configurados(monkeypatch):
    solicitudes = []
    guardados = []
    respuesta = {
        "properties": {
            "parameter": {
                codigo: {"20240101": 1.0}
                for codigo in config.NASA_POWER_PARAMETROS
            },
        },
    }
    monkeypatch.setattr(nasa_power, "ya_existe", lambda nombre, forzar: False)
    monkeypatch.setattr(
        nasa_power,
        "http_json",
        lambda metodo, url, **kwargs: solicitudes.append((metodo, url, kwargs)) or respuesta,
    )
    monkeypatch.setattr(
        nasa_power,
        "guardar_bronce",
        lambda df, nombre, fuente, origen: guardados.append(
            (df, nombre, fuente, origen)
        ),
    )

    nasa_power.extraer()

    metodo, url, kwargs = solicitudes[0]
    assert metodo == "GET"
    assert url == config.NASA_POWER_URL
    assert kwargs["params"]["start"] == config.FECHA_INICIO.strftime("%Y%m%d")
    assert kwargs["params"]["end"] == config.FECHA_FIN.strftime("%Y%m%d")
    assert kwargs["params"]["latitude"] == config.NASA_POWER_LATITUD
    assert kwargs["params"]["longitude"] == config.NASA_POWER_LONGITUD
    assert kwargs["params"]["time-standard"] == "UTC"
    assert len(guardados) == 1
    _, nombre, fuente, origen = guardados[0]
    assert nombre == nasa_power.NOMBRE
    assert fuente == "NASA POWER"
    assert str(config.NASA_POWER_LATITUD) in origen


def test_pipeline_incluye_nasa_power():
    from src import pipeline

    assert pipeline.nasa_power is nasa_power
