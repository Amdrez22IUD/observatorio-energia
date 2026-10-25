from src import perfilamiento


def test_perfilamiento_produce_diez_hallazgos():
    hallazgos = perfilamiento.generar_hallazgos()

    assert len(hallazgos) == 10
    assert any("XM generacion:" in hallazgo for hallazgo in hallazgos)
    assert any("XM aportes de energia:" in hallazgo for hallazgo in hallazgos)
    assert any("XM listado de recursos:" in hallazgo for hallazgo in hallazgos)
    assert any("XM precio:" in hallazgo for hallazgo in hallazgos)
    assert any("IDEAM temperatura:" in hallazgo for hallazgo in hallazgos)
    assert any("NASA POWER:" in hallazgo for hallazgo in hallazgos)
    assert any("NOAA ONI:" in hallazgo for hallazgo in hallazgos)


def test_perfilamiento_cli_imprime_numeracion_y_limitacion(capsys):
    perfilamiento.main()
    salida = capsys.readouterr().out

    assert "no representa el universo completo" in salida
    assert "10. NOAA ONI:" in salida
