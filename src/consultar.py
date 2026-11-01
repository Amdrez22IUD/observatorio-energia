"""
Ejecuta consultas de bronce y de oro con DuckDB.

Uso:
    python -m src.consultar
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import os       # os: funciones del sistema operativo; os.chdir() cambia de carpeta

import duckdb   # duckdb: motor SQL que lee archivos Parquet sin base de datos

from src import config       # configuracion central (para saber la carpeta raiz)
from src.utils import log    # mensajes con hora


def main() -> None:
    os.chdir(config.RAIZ)               # las rutas de los .sql son relativas a la raiz
    con = duckdb.connect()
    consultas_bronce = sorted((config.RAIZ / "consultas").glob("*.sql"))
    consultas_oro = sorted((config.RAIZ / "consultas" / "oro").glob("*.sql"))
    for archivo in consultas_bronce:
        log(f"Consulta bronce: {archivo.name}")
        sql = archivo.read_text(encoding="utf-8")
        print(con.sql(sql).df().to_string(index=False))
        print()
    if consultas_oro:
        base_oro = config.RAIZ / "data" / "observatorio.duckdb"
        if not base_oro.is_file():
            raise FileNotFoundError(
                f"No se encontró {base_oro}; ejecute primero `python -m src.transformar`."
            )
        con_oro = duckdb.connect(str(base_oro), read_only=True)
        for archivo in consultas_oro:
            log(f"Consulta oro: {archivo.name}")
            sql = archivo.read_text(encoding="utf-8")
            print(con_oro.sql(sql).df().to_string(index=False))
            print()
        con_oro.close()
    con.close()


if __name__ == "__main__":
    main()
