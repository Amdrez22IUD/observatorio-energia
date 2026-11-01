import pytest

from src import config
from src.quality.reporte import escribir_reporte_calidad
from src.transformar import _validar_bronce_disponible


def test_pipeline_informa_si_faltan_archivos_bronce(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DIR_BRONZE", tmp_path)

    with pytest.raises(FileNotFoundError, match="python -m src.pipeline"):
        _validar_bronce_disponible()


def test_reporte_consolida_fuentes_y_metricas(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DIR_DOCS", tmp_path)
    escribir_reporte_calidad([
        {
            "fuente": "EnerAndes",
            "anio": 2026,
            "problema": "Filas de bronce recibidas",
            "regla aplicada": "Detectar filas",
            "antes": 10,
            "despues": 10,
        },
        {
            "fuente": "EnerAndes",
            "anio": 2026,
            "problema": "Filas limpias",
            "regla aplicada": "Validar Pandera",
            "antes": 10,
            "despues": 8,
        },
        {
            "fuente": "EnerAndes",
            "anio": 2026,
            "problema": "Filas enviadas a cuarentena",
            "regla aplicada": "Conservar el motivo",
            "antes": 2,
            "despues": 2,
        },
    ])

    reporte = (tmp_path / "reporte_calidad.md").read_text(encoding="utf-8")

    assert "| EnerAndes | 10 | 8 | 2 |" in reporte
    assert "| 2026 | Filas limpias | Validar Pandera | 10 | 8 |" in reporte
