"""Limpieza, validación y escritura de las fuentes distintas de EnerAndes."""
from collections.abc import Callable

import pandas as pd

from src import config
from src.quality.esquemas import (
    ESQUEMA_IDEAM_PRECIPITACION,
    ESQUEMA_IDEAM_TEMPERATURA,
    ESQUEMA_NASA_POWER,
    ESQUEMA_NOAA_ONI,
    ESQUEMA_XM_APORTES,
    ESQUEMA_XM_DEMANDA,
    ESQUEMA_XM_EMBALSES,
    ESQUEMA_XM_GENERACION,
    ESQUEMA_XM_PRECIO_BOLSA,
    ESQUEMA_XM_RECURSOS,
)
from src.utils import log

LINAJE = ["_fuente", "_origen", "_extraido_en"]
HORAS_XM = [f"Hour{hora:02d}" for hora in range(1, 25)]
MESES_CENTRALES = {
    "DJF": 1,
    "JFM": 2,
    "FMA": 3,
    "MAM": 4,
    "AMJ": 5,
    "MJJ": 6,
    "JJA": 7,
    "JAS": 8,
    "ASO": 9,
    "SON": 10,
    "OND": 11,
    "NDJ": 12,
}


def _sin_linaje(bronce: pd.DataFrame) -> pd.DataFrame:
    return bronce.drop(columns=LINAJE, errors="ignore").copy()


def _razones(
    tabla: pd.DataFrame,
    reglas: list[tuple[pd.Series, str]],
) -> pd.Series:
    resultado = pd.Series("", index=tabla.index, dtype="string")
    for mascara, motivo in reglas:
        filas = mascara.reindex(tabla.index, fill_value=False).fillna(False)
        resultado.loc[filas] = resultado.loc[filas].map(
            lambda actual: f"{actual}; {motivo}" if actual else motivo
        )
    return resultado


def _metricas(
    fuente: str,
    total_entrada: int,
    total_salida: int,
    total_cuarentena: int,
    duplicados: int = 0,
    invalidos: int = 0,
    vacios: int = 0,
) -> list[dict[str, int | str]]:
    return [
        {"fuente": fuente, "problema": "Registros en la fuente", "regla aplicada":
         "Clasificar las filas entre plata y cuarentena", "antes": total_entrada,
         "despues": total_salida + total_cuarentena},
        {"fuente": fuente, "problema": "Valores vacíos no imputables", "regla aplicada":
         "Conservarlos como nulos; no inventar valores", "antes": vacios, "despues": vacios},
        {"fuente": fuente, "problema": "Filas duplicadas o conflictos de llave",
         "regla aplicada": "Conservar una fila o separar el conflicto", "antes": duplicados,
         "despues": 0},
        {"fuente": fuente, "problema": "Filas inválidas enviadas a cuarentena",
         "regla aplicada": "Preservar la fila con el motivo de rechazo", "antes": invalidos,
         "despues": total_cuarentena},
        {"fuente": fuente, "problema": "Filas válidas", "regla aplicada":
         "Validar el esquema Pandera antes de guardar", "antes": total_entrada,
         "despues": total_salida},
    ]


def _separar_cuarentena(
    tabla: pd.DataFrame,
    reglas: list[tuple[pd.Series, str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    motivos = _razones(tabla, reglas)
    invalida = motivos.ne("")
    limpias = tabla.loc[~invalida].copy()
    cuarentena = tabla.loc[invalida].copy()
    if not cuarentena.empty:
        cuarentena["motivo_cuarentena"] = motivos.loc[invalida]
    return limpias, cuarentena


def _normalizar_numero(serie: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    texto = serie.astype("string").str.strip()
    vacios = serie.isna() | texto.eq("")
    numeros = pd.to_numeric(texto.mask(vacios), errors="coerce")
    no_numericos = ~vacios & numeros.isna()
    return numeros.astype("float64"), vacios, no_numericos


def limpiar_xm_horario(
    bronce: pd.DataFrame,
    columna_valor: str,
    columna_codigo: str = "codigo",
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int | str]]]:
    """Convierte una métrica XM ancha en una fila por entidad, fecha y hora."""
    fuente = _sin_linaje(bronce)
    faltantes = {"Date", *HORAS_XM} - set(fuente.columns)
    if "code" not in fuente.columns and "Id" not in fuente.columns:
        faltantes.add("code o Id")
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas de XM horario: {sorted(faltantes)}")
    campo_codigo = "code" if "code" in fuente.columns else "Id"
    ids = ["Date", campo_codigo]
    if "Id" in fuente.columns:
        ids.append("Id")
    ids = list(dict.fromkeys(ids))
    ancho = fuente[ids + HORAS_XM].copy()
    ancho["Date"] = pd.to_datetime(ancho["Date"], errors="coerce").dt.normalize()
    largo = ancho.melt(
        id_vars=ids,
        value_vars=HORAS_XM,
        var_name="_hora",
        value_name="_valor",
    )
    largo["hora"] = largo["_hora"].str.extract(r"(\d+)$", expand=False).astype("int64")
    largo["_valor"], vacios, no_numericos = _normalizar_numero(largo["_valor"])
    salida = pd.DataFrame({
        "fecha": largo["Date"],
        "hora": largo["hora"],
        columna_codigo: largo[campo_codigo].astype("string").str.strip(),
        columna_valor: largo["_valor"],
    })
    fecha_invalida = salida["fecha"].isna()
    codigo_invalido = salida[columna_codigo].isna() | salida[columna_codigo].eq("")
    reglas = [
        (fecha_invalida, "fecha inválida"),
        (codigo_invalido, "código de entidad vacío"),
        (no_numericos, "valor horario no numérico"),
    ]
    llave = ["fecha", "hora", columna_codigo]
    duplicadas = salida.duplicated(llave, keep="first")
    reglas.append((duplicadas, "llave fecha/hora/entidad duplicada"))
    limpias, cuarentena = _separar_cuarentena(salida, reglas)
    metricas = _metricas(
        "XM horario",
        len(fuente),
        len(limpias),
        len(cuarentena),
        duplicados=int(duplicadas.sum()),
        invalidos=int((fecha_invalida | codigo_invalido | no_numericos).sum()),
        vacios=int(vacios.sum()),
    )
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def limpiar_xm_diario(
    bronce: pd.DataFrame,
    nombre_valor: str,
    valor_limitado: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int | str]]]:
    """Normaliza las series diarias de embalses y aportes de XM."""
    fuente = _sin_linaje(bronce)
    requeridas = {"Date", "Id", "Value"}
    faltantes = requeridas - set(fuente.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas de XM diario: {sorted(faltantes)}")
    valor, vacios, no_numericos = _normalizar_numero(fuente["Value"])
    salida = pd.DataFrame({
        "fecha": pd.to_datetime(fuente["Date"], errors="coerce").dt.normalize(),
        "id": fuente["Id"].astype("string").str.strip(),
        nombre_valor: valor,
    })
    fecha_invalida = salida["fecha"].isna()
    id_invalido = salida["id"].isna() | salida["id"].eq("")
    reglas: list[tuple[pd.Series, str]] = [
        (fecha_invalida, "fecha inválida"),
        (id_invalido, "identificador vacío"),
        (vacios, "valor diario vacío"),
        (no_numericos, "valor diario no numérico"),
        (valor.lt(0), "valor diario negativo"),
    ]
    if valor_limitado:
        reglas.append((valor.gt(1), "porcentaje superior a 1"))
    duplicadas = salida.duplicated(["fecha", "id"], keep="first")
    reglas.append((duplicadas, "llave fecha/identificador duplicada"))
    limpias, cuarentena = _separar_cuarentena(salida, reglas)
    invalidas = fecha_invalida | id_invalido | vacios | no_numericos | valor.lt(0)
    if valor_limitado:
        invalidas |= valor.gt(1)
    metricas = _metricas(
        "XM diario",
        len(salida),
        len(limpias),
        len(cuarentena),
        duplicados=int(duplicadas.sum()),
        invalidos=int(invalidas.sum()),
        vacios=int(vacios.sum()),
    )
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def limpiar_xm_recursos(
    bronce: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int | str]]]:
    """Normaliza el catálogo de recursos y resuelve sus códigos repetidos."""
    fuente = _sin_linaje(bronce)
    columnas = {
        "Code": "codigo_recurso",
        "Name": "nombre_recurso",
        "Type": "tipo",
        "Disp": "disponibilidad",
        "RecType": "tipo_recurso",
        "CompanyCode": "codigo_empresa",
        "EnerSource": "fuente_energia",
        "OperStartdate": "fecha_inicio_operacion",
        "State": "estado",
    }
    faltantes = set(columnas) - set(fuente.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas del catálogo XM: {sorted(faltantes)}")
    salida = fuente[list(columnas)].rename(columns=columnas).copy()
    for columna in set(salida.columns) - {"fecha_inicio_operacion"}:
        salida[columna] = salida[columna].astype("string").str.strip()
    fecha_texto = salida["fecha_inicio_operacion"].astype("string").str.strip()
    fecha_vacia = fecha_texto.isna() | fecha_texto.eq("")
    fecha_operacion = pd.to_datetime(fecha_texto.mask(fecha_vacia), errors="coerce")
    fecha_invalida = ~fecha_vacia & fecha_operacion.isna()
    salida["fecha_inicio_operacion"] = fecha_operacion
    codigo_vacio = salida["codigo_recurso"].isna() | salida["codigo_recurso"].eq("")
    nombre_vacio = salida["nombre_recurso"].isna() | salida["nombre_recurso"].eq("")
    tipo_vacio = salida["tipo"].isna() | salida["tipo"].eq("")
    exactos = salida.duplicated(keep="first")
    sin_exactos = salida.loc[~exactos].copy()
    codigo_repetido = sin_exactos.duplicated(["codigo_recurso"], keep="first")
    reglas = [
        (sin_exactos["codigo_recurso"].isna() | sin_exactos["codigo_recurso"].eq(""),
         "código de recurso vacío"),
        (sin_exactos["nombre_recurso"].isna() | sin_exactos["nombre_recurso"].eq(""),
         "nombre de recurso vacío"),
        (sin_exactos["tipo"].isna() | sin_exactos["tipo"].eq(""),
         "tipo de recurso vacío"),
        (~fecha_vacia.loc[sin_exactos.index] & sin_exactos["fecha_inicio_operacion"].isna(),
         "fecha de inicio de operación inválida"),
        (codigo_repetido, "código asociado a más de un registro"),
    ]
    limpias, cuarentena = _separar_cuarentena(sin_exactos, reglas)
    metricas = _metricas(
        "XM catálogo de recursos",
        len(salida),
        len(limpias),
        len(cuarentena),
        duplicados=int(exactos.sum() + codigo_repetido.sum()),
        invalidos=int((codigo_vacio | nombre_vacio | tipo_vacio | fecha_invalida).sum()),
    )
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def limpiar_ideam(
    bronce: pd.DataFrame,
    mediciones: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int | str]]]:
    """Convierte fechas y mediciones IDEAM a tipos nativos y conserva estación/municipio."""
    fuente = _sin_linaje(bronce)
    columnas_fijas = {
        "codigoestacion": "codigo_estacion",
        "nombreestacion": "nombre_estacion",
        "municipio": "municipio",
        "latitud": "latitud",
        "longitud": "longitud",
        "fecha": "fecha",
        "n_obs": "n_observaciones",
    }
    requeridas = set(columnas_fijas) | set(mediciones)
    faltantes = requeridas - set(fuente.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas de IDEAM: {sorted(faltantes)}")
    orden_columnas = [
        "codigoestacion", "nombreestacion", "municipio", "latitud", "longitud",
        "fecha", *mediciones, "n_obs",
    ]
    salida = fuente[orden_columnas].rename(
        columns={**columnas_fijas, **mediciones}
    ).copy()
    for columna in ["codigo_estacion", "nombre_estacion", "municipio"]:
        salida[columna] = salida[columna].astype("string").str.strip()
    salida["municipio"] = salida["municipio"].str.title()
    salida["fecha"] = pd.to_datetime(salida["fecha"], errors="coerce").dt.normalize()
    valores_vacios = pd.Series(False, index=salida.index)
    no_numericos = pd.Series(False, index=salida.index)
    reglas: list[tuple[pd.Series, str]] = [
        (salida["fecha"].isna(), "fecha inválida"),
        (salida["codigo_estacion"].isna() | salida["codigo_estacion"].eq(""),
         "código de estación vacío"),
        (salida["nombre_estacion"].isna() | salida["nombre_estacion"].eq(""),
         "nombre de estación vacío"),
        (salida["municipio"].isna() | salida["municipio"].eq(""),
         "municipio de estación vacío"),
    ]
    numericas = ["latitud", "longitud", "n_observaciones", *mediciones.values()]
    invalidas = pd.Series(False, index=salida.index)
    for columna in numericas:
        original = salida[columna]
        valor, vacio, no_numerico = _normalizar_numero(original)
        salida[columna] = valor
        valores_vacios |= vacio
        no_numericos |= no_numerico
        invalidas |= vacio | no_numerico
        reglas.append((vacio, f"{columna} vacío"))
        reglas.append((no_numerico, f"{columna} no numérico"))
    reglas.extend([
        (~salida["latitud"].between(-90, 90), "latitud fuera de rango"),
        (~salida["longitud"].between(-180, 180), "longitud fuera de rango"),
        (salida["n_observaciones"].lt(1)
         | salida["n_observaciones"].mod(1).ne(0), "conteo de observaciones inválido"),
    ])
    for columna in mediciones.values():
        if columna == "precipitacion_mm":
            reglas.append((salida[columna].lt(0), "precipitación negativa"))
        else:
            reglas.append((salida[columna].lt(-100) | salida[columna].gt(100),
                           f"{columna} fuera de rango"))
    if "temperatura_minima_c" in salida and "temperatura_maxima_c" in salida:
        reglas.append(
            (salida["temperatura_minima_c"].gt(salida["temperatura_maxima_c"]),
             "temperatura mínima superior a la máxima")
        )
    if {
        "temperatura_minima_c", "temperatura_promedio_c", "temperatura_maxima_c"
    }.issubset(salida.columns):
        reglas.extend([
            (salida["temperatura_promedio_c"].lt(salida["temperatura_minima_c"]),
             "temperatura promedio inferior a la mínima"),
            (salida["temperatura_promedio_c"].gt(salida["temperatura_maxima_c"]),
             "temperatura promedio superior a la máxima"),
        ])
    duplicadas = salida.duplicated(["fecha", "codigo_estacion"], keep="first")
    reglas.append((duplicadas, "llave estación/fecha duplicada"))
    limpias, cuarentena = _separar_cuarentena(salida, reglas)
    for columna in numericas:
        limpias[columna] = limpias[columna].astype("int64" if columna == "n_observaciones" else "float64")
    metricas = _metricas(
        "IDEAM",
        len(salida),
        len(limpias),
        len(cuarentena),
        duplicados=int(duplicadas.sum()),
        invalidos=int(sum(int(mascara.fillna(False).sum()) for mascara, _ in reglas)),
        vacios=int(valores_vacios.sum()),
    )
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def fase_enso(oni: float) -> str:
    if oni >= 0.5:
        return "El Niño"
    if oni <= -0.5:
        return "La Niña"
    return "Neutral"


def limpiar_noaa(
    bronce: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int | str]]]:
    """Asigna cada trimestre ONI a su mes central según el año del archivo."""
    fuente = _sin_linaje(bronce)
    requeridas = {"SEAS", "YR", "ANOM"}
    faltantes = requeridas - set(fuente.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas de NOAA: {sorted(faltantes)}")
    temporadas = fuente["SEAS"].astype("string").str.strip().str.upper()
    anio = pd.to_numeric(fuente["YR"], errors="coerce")
    oni, oni_vacio, oni_no_numerico = _normalizar_numero(fuente["ANOM"])
    mes = temporadas.map(MESES_CENTRALES)
    fecha = pd.to_datetime(
        {"year": anio, "month": mes, "day": 1},
        errors="coerce",
    )
    salida = pd.DataFrame({
        "fecha": fecha,
        "oni": oni,
        "fase_enso": oni.map(fase_enso),
    })
    temporada_invalida = mes.isna()
    reglas = [
        (temporada_invalida, "trimestre ONI no reconocido"),
        (salida["fecha"].isna(), "año o mes central inválido"),
        (oni_vacio, "anomalía ONI vacía"),
        (oni_no_numerico, "anomalía ONI no numérica"),
        (~oni.between(-5, 5), "anomalía ONI fuera de rango"),
    ]
    duplicadas = salida.duplicated(["fecha"], keep="first")
    reglas.append((duplicadas, "mes central duplicado"))
    limpias, cuarentena = _separar_cuarentena(salida, reglas)
    metricas = _metricas(
        "NOAA ONI",
        len(salida),
        len(limpias),
        len(cuarentena),
        duplicados=int(duplicadas.sum()),
        invalidos=int((temporada_invalida | salida["fecha"].isna()
                       | oni_vacio | oni_no_numerico | ~oni.between(-5, 5)).sum()),
        vacios=int(oni_vacio.sum()),
    )
    metricas.append({
        "fuente": "NOAA ONI",
        "problema": "Trimestres asignados al mes central",
        "antes": int(temporadas.isin(MESES_CENTRALES).sum()),
        "despues": int(limpias["fecha"].nunique()),
    })
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def limpiar_nasa_power(
    bronce: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, int | str]]]:
    """Convierte fechas y valores NASA POWER; -999 se conserva como dato nulo."""
    fuente = _sin_linaje(bronce)
    columnas = ["fecha", *config.NASA_POWER_PARAMETROS.values()]
    faltantes = set(columnas) - set(fuente.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas de NASA POWER: {sorted(faltantes)}")
    salida = fuente[columnas].copy()
    salida["fecha"] = pd.to_datetime(salida["fecha"], format="%Y%m%d", errors="coerce")
    reglas: list[tuple[pd.Series, str]] = [
        (salida["fecha"].isna(), "fecha inválida"),
    ]
    vacios_total = 0
    no_numericos_total = 0
    for columna in config.NASA_POWER_PARAMETROS.values():
        valor, vacios, no_numericos = _normalizar_numero(salida[columna])
        sentinel = valor.eq(-999)
        vacios_total += int(vacios.sum() + sentinel.sum())
        no_numericos_total += int(no_numericos.sum())
        valor = valor.mask(sentinel)
        salida[columna] = valor
        reglas.append((no_numericos, f"{columna} no numérico"))
        if columna != "temperatura_2m_c":
            reglas.append((valor.lt(0) & ~sentinel & valor.notna(), f"{columna} negativo"))
    duplicadas = salida.duplicated(["fecha"], keep="first")
    reglas.append((duplicadas, "fecha diaria duplicada"))
    limpias, cuarentena = _separar_cuarentena(salida, reglas)
    for columna in config.NASA_POWER_PARAMETROS.values():
        limpias[columna] = limpias[columna].astype("float64")
    metricas = _metricas(
        "NASA POWER",
        len(salida),
        len(limpias),
        len(cuarentena),
        duplicados=int(duplicadas.sum()),
        invalidos=no_numericos_total + int(duplicadas.sum()),
        vacios=vacios_total,
    )
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def _guardar_tabla(
    nombre: str,
    bronce: pd.DataFrame,
    limpiar: Callable,
    esquema,
    *argumentos,
) -> list[dict[str, int | str]]:
    limpias, cuarentena, metricas = limpiar(bronce, *argumentos)
    esquema.validate(limpias, lazy=True)
    for metrica in metricas:
        metrica["fuente"] = nombre
    ruta = config.DIR_SILVER / f"{nombre}.parquet"
    limpias.to_parquet(ruta, index=False)
    ruta_cuarentena = config.DIR_SILVER / f"{nombre}_cuarentena.parquet"
    if not cuarentena.empty:
        cuarentena.to_parquet(ruta_cuarentena, index=False)
    elif ruta_cuarentena.exists():
        ruta_cuarentena.unlink()
    log(
        f"{nombre}: Pandera OK, {len(limpias):,} filas limpias, "
        f"{len(cuarentena):,} en cuarentena"
    )
    return metricas


def main() -> list[dict[str, int | str]]:
    config.DIR_SILVER.mkdir(parents=True, exist_ok=True)
    trabajos = [
        ("xm_precio_bolsa_horario", "xm_precio_bolsa", limpiar_xm_horario,
         ESQUEMA_XM_PRECIO_BOLSA, ("precio_bolsa", "codigo")),
        ("xm_demanda_horaria", "xm_demanda", limpiar_xm_horario,
         ESQUEMA_XM_DEMANDA, ("demanda", "codigo")),
        ("xm_generacion_recurso_horaria", "xm_generacion_recurso", limpiar_xm_horario,
         ESQUEMA_XM_GENERACION, ("generacion", "codigo_recurso")),
        ("xm_embalses_diarios", "xm_embalses", limpiar_xm_diario,
         ESQUEMA_XM_EMBALSES, ("porcentaje_util", True)),
        ("xm_aportes_energia_diarios", "xm_aportes_energia", limpiar_xm_diario,
         ESQUEMA_XM_APORTES, ("aportes_energia", False)),
        ("xm_listado_recursos", "xm_listado_recursos", limpiar_xm_recursos,
         ESQUEMA_XM_RECURSOS, ()),
        ("ideam_precipitacion_diaria", "ideam_precipitacion_diaria", limpiar_ideam,
         ESQUEMA_IDEAM_PRECIPITACION, ({"precipitacion_mm": "precipitacion_mm"},)),
        ("ideam_temperatura_diaria", "ideam_temperatura_diaria", limpiar_ideam,
         ESQUEMA_IDEAM_TEMPERATURA, ({
             "temperatura_promedio_c": "temperatura_promedio_c",
             "temperatura_minima_c": "temperatura_minima_c",
             "temperatura_maxima_c": "temperatura_maxima_c",
         },)),
        ("noaa_oni_mensual", "noaa_oni", limpiar_noaa, ESQUEMA_NOAA_ONI, ()),
        ("nasa_power_clima_diario", "nasa_power_clima_diario", limpiar_nasa_power,
         ESQUEMA_NASA_POWER, ()),
    ]
    metricas_totales = []
    for salida, origen, funcion, esquema, argumentos in trabajos:
        bronce = pd.read_parquet(config.DIR_BRONZE / f"{origen}.parquet")
        metricas_totales.extend(
            _guardar_tabla(salida, bronce, funcion, esquema, *argumentos)
        )
    print(f"{'fuente':<22}{'problema':<42}{'antes':>10}{'después':>10}")
    for metrica in metricas_totales:
        print(
            f"{metrica['fuente']:<22}{metrica['problema']:<42}"
            f"{metrica['antes']:>10}{metrica['despues']:>10}"
        )
    return metricas_totales


if __name__ == "__main__":
    main()
