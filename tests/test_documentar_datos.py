import pandas as pd

from src import config, documentar_datos


def test_exportar_muestras_lleva_hasta_200_filas_incluido_enerandes(
    tmp_path,
    monkeypatch,
):
    bronze = tmp_path / "bronze"
    samples = tmp_path / "sample"
    bronze.mkdir()
    pd.DataFrame({"Date": range(205), "Value": range(205)}).to_parquet(
        bronze / "xm_embalses.parquet",
        index=False,
    )
    pd.DataFrame({"col_0": range(205)}).to_parquet(
        bronze / "enerandes_ventas_2023.parquet",
        index=False,
    )
    monkeypatch.setattr(config, "DIR_BRONZE", bronze)
    monkeypatch.setattr(documentar_datos, "DIR_SAMPLE", samples)

    assert documentar_datos.exportar_muestras() == [
        "enerandes_ventas_2023",
        "xm_embalses",
    ]
    muestra = pd.read_csv(samples / "xm_embalses.csv")
    assert len(muestra) == 200
    assert muestra.iloc[0]["Date"] == 0
    muestra_enerandes = pd.read_csv(samples / "enerandes_ventas_2023.csv")
    assert len(muestra_enerandes) == 200


def test_reporte_incluye_perfil_por_columna_y_archivos_enerandes(
    tmp_path,
    monkeypatch,
):
    bronze = tmp_path / "bronze"
    docs = tmp_path / "docs"
    bronze.mkdir()
    pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-02", "2024-01-02"],
        "Value": ["1", None, "1"],
    }).to_parquet(bronze / "xm_embalses.parquet", index=False)
    monkeypatch.setattr(config, "DIR_BRONZE", bronze)
    monkeypatch.setattr(documentar_datos, "RUTA_REPORTE", docs / "perfilamiento.md")

    reporte = documentar_datos.generar_reporte()

    assert "- Filas: **3**" in reporte
    assert "- Columnas: **2**" in reporte
    assert "Filas duplicadas completas: **0**" in reporte
    assert "| `Value` | `str` | 1 | 33.33% |" in reporte
    assert "2024-01-01 a 2024-01-02" in reporte
    assert "recreativo y educativo" in reporte
    assert "## Archivos esperados no encontrados" in reporte
