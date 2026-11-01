import pandas as pd

from src.silver.enerandes import _periodo_mensual, limpiar


def _hoja_2024(rows: list[list[object]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=[f"col_{indice}" for indice in range(8)])


def test_normaliza_formatos_mensuales_conocidos():
    assert _periodo_mensual("2024-03") == "2024-03"
    assert _periodo_mensual("mar-24") == "2024-03"
    assert _periodo_mensual("03/2024") == "2024-03"
    assert _periodo_mensual("aug-24") == "2024-08"


def test_interpreta_fecha_completa_con_dia_primero():
    assert _periodo_mensual("01/03/2026") == "2026-03"


def test_convierte_energia_mwh_a_kwh():
    bronce = _hoja_2024([
        ["PERIODO", "MUNICIPIO", "SEGMENTO CLIENTE", "MODALIDAD",
         "ENERGIA", "UNIDAD", "VALOR ($)", "NUM CLIENTES"],
        ["2024-03", "Bello", "Comercial", "Bolsa", "1.5", "MWh", "2000", "3"],
    ])

    limpias, cuarentena, _ = limpiar(bronce, anio=2024)

    assert len(cuarentena) == 0
    assert limpias.loc[0, "energia_kwh"] == 1500


def test_fila_con_energia_vacia_se_conserva_en_cuarentena():
    bronce = _hoja_2024([
        ["PERIODO", "MUNICIPIO", "SEGMENTO CLIENTE", "MODALIDAD",
         "ENERGIA", "UNIDAD", "VALOR ($)", "NUM CLIENTES"],
        ["2024-03", "Bello", "Comercial", "Bolsa", None, "kWh", "2000", "3"],
    ])

    limpias, cuarentena, _ = limpiar(bronce, anio=2024)

    assert limpias.empty
    assert cuarentena.loc[0, "motivo_cuarentena"] == "energía vacía"


def test_fila_con_fecha_vacia_no_se_descarta():
    bronce = _hoja_2024([
        ["PERIODO", "MUNICIPIO", "SEGMENTO CLIENTE", "MODALIDAD",
         "ENERGIA", "UNIDAD", "VALOR ($)", "NUM CLIENTES"],
        [None, "Bello", "Comercial", "Bolsa", "100", "kWh", "2000", "3"],
    ])

    limpias, cuarentena, _ = limpiar(bronce, anio=2024)

    assert limpias.empty
    assert len(cuarentena) == 1
    assert "fecha ausente" in cuarentena.loc[0, "motivo_cuarentena"]


def test_encuentra_encabezado_tras_preambulo_y_excluye_total():
    bronce = pd.DataFrame([
        ["Reporte mensual", None, None, None, None, None, None],
        ["Fuente interna", None, None, None, None, None, None],
        ["MES", "MUNICIPIO", "SEGMENTO", "TIPO COMPRA", "CONSUMO (KWH)",
         "FACTURADO", "USUARIOS"],
        ["06/2025", "Medellín", "Residencial", "Contrato", "100", "500", "2"],
        ["TOTAL", None, None, None, "100", "500", "2"],
    ], columns=[f"col_{indice}" for indice in range(7)])

    limpias, cuarentena, _ = limpiar(bronce, anio=2025)

    assert len(limpias) == 1
    assert len(cuarentena) == 0
    assert limpias.loc[0, "periodo"] == "2025-06"


def test_municipio_no_reconocido_se_conserva_en_cuarentena():
    bronce = _hoja_2024([
        ["PERIODO", "MUNICIPIO", "SEGMENTO CLIENTE", "MODALIDAD",
         "ENERGIA", "UNIDAD", "VALOR ($)", "NUM CLIENTES"],
        ["2024-03", "Municipio desconocido", "Comercial", "Bolsa", "100", "kWh", "2000", "3"],
    ])

    limpias, cuarentena, _ = limpiar(bronce, anio=2024)

    assert limpias.empty
    assert len(cuarentena) == 1
    assert "DIVIPOLA" in cuarentena.loc[0, "motivo_cuarentena"]


def test_segmento_no_reconocido_se_conserva_en_cuarentena():
    bronce = _hoja_2024([
        ["PERIODO", "MUNICIPIO", "SEGMENTO CLIENTE", "MODALIDAD",
         "ENERGIA", "UNIDAD", "VALOR ($)", "NUM CLIENTES"],
        ["2024-03", "Bello", "Otro", "Bolsa", "100", "kWh", "2000", "3"],
    ])

    limpias, cuarentena, _ = limpiar(bronce, anio=2024)

    assert limpias.empty
    assert "segmento no reconocido" in cuarentena.loc[0, "motivo_cuarentena"]
