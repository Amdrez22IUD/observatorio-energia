from src.extract import xm


def test_aplanar_datos_horarios():
    respuesta = {
        "Items": [{
            "Date": "2024-01-01",
            "HourlyEntities": [{
                "Id": "Sistema",
                "Values": {"Hour01": "10.5", "Hour02": "11.0"},
            }],
        }],
    }

    assert xm.aplanar(respuesta, "hourly") == [{
        "Date": "2024-01-01",
        "Id": "Sistema",
        "Hour01": "10.5",
        "Hour02": "11.0",
    }]


def test_aplanar_datos_diarios():
    respuesta = {
        "Items": [{
            "Date": "2024-01-01",
            "DailyEntities": [{"Id": "Sistema", "Value": "123.4"}],
        }],
    }

    assert xm.aplanar(respuesta, "daily") == [{
        "Date": "2024-01-01",
        "Id": "Sistema",
        "Value": "123.4",
    }]


def test_aplanar_listado_de_recursos():
    respuesta = {
        "Items": [{
            "Date": "2026-10-25",
            "ListEntities": [{
                "Id": "Sistema",
                "Values": {"Code": "2QBW", "Name": "EL POPAL"},
            }],
        }],
    }

    assert xm.aplanar(respuesta, "lists") == [{
        "Date": "2026-10-25",
        "Id": "Sistema",
        "Code": "2QBW",
        "Name": "EL POPAL",
    }]


def test_extraer_listado_solicita_endpoint_lists_sin_fechas(monkeypatch):
    solicitudes = []
    guardados = []
    respuesta = {
        "Items": [{
            "Date": "2026-10-25",
            "ListEntities": [{
                "Id": "Sistema",
                "Values": {"Code": "2QBW", "Name": "EL POPAL"},
            }],
        }],
    }

    monkeypatch.setattr(xm, "ya_existe", lambda nombre, forzar: False)
    monkeypatch.setattr(
        xm,
        "http_json",
        lambda metodo, url, **kwargs: solicitudes.append((metodo, url, kwargs)) or respuesta,
    )
    monkeypatch.setattr(
        xm,
        "guardar_bronce",
        lambda df, nombre, fuente, origen: guardados.append((df, nombre, fuente, origen)),
    )

    xm.extraer_metrica("ListadoRecursos", "Sistema", "lists", "xm_listado_recursos", False)

    assert solicitudes == [(
        "POST",
        "https://servapibi.xm.com.co/lists",
        {"json": {"MetricId": "ListadoRecursos", "Entity": "Sistema"}},
    )]
    assert len(guardados) == 1
    df, nombre, fuente, _ = guardados[0]
    assert df.loc[0, "Code"] == "2QBW"
    assert nombre == "xm_listado_recursos"
    assert fuente == "XM"
