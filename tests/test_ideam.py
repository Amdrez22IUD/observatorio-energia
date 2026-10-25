from datetime import date

from src import config
from src.extract import ideam


def test_precipitacion_filtra_antioquia_y_suma_por_dia():
    consulta = ideam.consulta_soql(date(2025, 1, 1), date(2025, 1, 7), 0)

    assert "departamento = 'ANTIOQUIA'" in consulta["$where"]
    assert "sum(valorobservado) AS precipitacion_mm" in consulta["$select"]
    assert "date_trunc_ymd(fechaobservacion) AS fecha" in consulta["$select"]


def test_temperatura_resume_minimo_promedio_y_maximo_por_dia():
    consulta = ideam.consulta_temperatura(date(2025, 1, 1), date(2025, 1, 7), 0)

    assert "avg(valorobservado) AS temperatura_promedio_c" in consulta["$select"]
    assert "min(valorobservado) AS temperatura_minima_c" in consulta["$select"]
    assert "max(valorobservado) AS temperatura_maxima_c" in consulta["$select"]
    assert "descripcionsensor IN (" in consulta["$where"]
    assert "2025-01-01T00:00:00" in consulta["$where"]
    assert consulta["$limit"] == ideam.PAGINA


def test_extraer_invoca_precipitacion_y_temperatura(monkeypatch):
    invocaciones = []
    monkeypatch.setattr(
        ideam,
        "_extraer_dataset",
        lambda nombre, url, consulta, forzar: invocaciones.append(
            (nombre, url, consulta, forzar)
        ),
    )

    ideam.extraer(forzar=True)

    assert [llamada[0] for llamada in invocaciones] == [
        ideam.NOMBRE,
        ideam.NOMBRE_TEMPERATURA,
    ]
    assert invocaciones[1][1] == config.IDEAM_TEMPERATURA_URL
    assert invocaciones[1][3] is True


def test_extraer_dataset_guarda_resultado_paginado(monkeypatch):
    guardados = []
    monkeypatch.setattr(config, "IDEAM_FECHA_INICIO", date(2025, 1, 1))
    monkeypatch.setattr(config, "FECHA_FIN", date(2025, 1, 1))
    monkeypatch.setattr(ideam, "ya_existe", lambda nombre, forzar: False)
    monkeypatch.setattr(ideam, "http_json", lambda *args, **kwargs: [{"fecha": "2025-01-01"}])
    monkeypatch.setattr(
        ideam,
        "guardar_bronce",
        lambda df, nombre, fuente, origen: guardados.append(
            (df, nombre, fuente, origen)
        ),
    )

    ideam._extraer_dataset(
        ideam.NOMBRE_TEMPERATURA,
        config.IDEAM_TEMPERATURA_URL,
        ideam.consulta_temperatura,
        False,
    )

    assert len(guardados) == 1
    df, nombre, fuente, origen = guardados[0]
    assert df.loc[0, "fecha"] == "2025-01-01"
    assert nombre == ideam.NOMBRE_TEMPERATURA
    assert fuente == "IDEAM"
    assert origen == config.IDEAM_TEMPERATURA_URL
