"""
Capa PLATA: limpia las hojas 2023–2026 del Excel de ventas de EnerAndes.

Lee los cuatro Parquet de bronce, aplica las reglas comunes y MIDE cada
problema antes y despues.
Luego valida el resultado con pandera (src/quality/esquemas.py) y guarda:
  - data/silver/enerandes_ventas.parquet       las filas limpias
  - data/silver/enerandes_cuarentena.parquet   las filas que no se pueden usar
  - docs/reporte_calidad.md                    la tabla de metricas antes y despues

En bronce no se modifica nada: aqui se trabaja sobre una copia.

Uso:
    python -m src.silver.enerandes
"""
# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import re
import unicodedata      # unicodedata: separa una letra de su tilde (para quitar tildes)
from datetime import datetime

import pandas as pd     # pandas: tablas

from src import config                           # rutas de las carpetas
from src.quality.esquemas import ESQUEMA_VENTAS  # las reglas que debe cumplir la tabla limpia
from src.utils import log                        # mensajes con hora

LINAJE = ["_fuente", "_origen", "_extraido_en"]  # columnas que agrego guardar_bronce()

# Municipio (escrito sin tildes y en minuscula) -> (codigo DIVIPOLA, nombre oficial)
MUNICIPIOS = {
    "medellin": ("05001", "Medellín"),
    "santa fe de antioquia": ("05042", "Santa Fe de Antioquia"),
    "apartado": ("05045", "Apartadó"),
    "bello": ("05088", "Bello"),
    "caldas": ("05129", "Caldas"),
    "caucasia": ("05154", "Caucasia"),
    "copacabana": ("05212", "Copacabana"),
    "envigado": ("05266", "Envigado"),
    "girardota": ("05308", "Girardota"),
    "itagui": ("05360", "Itagüí"),
    "la estrella": ("05380", "La Estrella"),
    "marinilla": ("05440", "Marinilla"),
    "rionegro": ("05615", "Rionegro"),
    "sabaneta": ("05631", "Sabaneta"),
    "turbo": ("05837", "Turbo"),
}
# Otras formas de escribir el mismo municipio -> la forma de la lista de arriba
ALIAS_MUNICIPIO = {
    "rio negro": "rionegro",
    "rionegro (ant)": "rionegro",
    "medellin d.e.": "medellin",
    "sta fe de antioquia": "santa fe de antioquia",
    "santafe de antioquia": "santa fe de antioquia",
}
# Formas de escribir el segmento y el tipo de compra -> valor estandar
SEGMENTOS = {"residencial": "Residencial", "resid.": "Residencial",
             "comercial": "Comercial", "industrial": "Industrial", "ind": "Industrial"}
TIPOS_COMPRA = {"bolsa": "Bolsa", "contrato": "Contrato", "contratos": "Contrato"}


# ---------------------------------------------------------------------------
# FUNCIONES DE APOYO
# ---------------------------------------------------------------------------
def sin_tildes(texto: str) -> str:
    """'Itagüí' -> 'itagui': minuscula, sin espacios a los lados y sin tildes."""
    # texto.strip() quita los espacios de los lados: ' ITAGÜÍ ' -> 'ITAGÜÍ'
    # .lower() lo pasa a minuscula: 'ITAGÜÍ' -> 'itagüí'
    # normalize("NFD", ...) separa cada letra de su tilde: 'í' queda como 'i' + tilde
    letras = unicodedata.normalize("NFD", texto.strip().lower())
    # (c for c in letras if ...) recorre las letras una por una y salta las tildes
    # (las tildes son de la categoria "Mn"); "".join(...) las vuelve a unir en un texto
    return "".join(c for c in letras if unicodedata.category(c) != "Mn")


def clave_municipio(texto) -> str | None:
    """Convierte cualquier forma de escribir el municipio en la clave de MUNICIPIOS."""
    # pd.isna(texto) es True si la celda esta vacia: no hay municipio que buscar
    if pd.isna(texto):
        # None significa "sin valor"
        return None
    # Quita espacios, mayusculas y tildes: ' Rio Negro ' -> 'rio negro'
    clave = sin_tildes(texto)
    # .get(clave, clave) busca la clave en ALIAS_MUNICIPIO:
    # si la encuentra ('rio negro'), devuelve su valor ('rionegro');
    # si no la encuentra ('bello'), devuelve la misma clave ('bello')
    return ALIAS_MUNICIPIO.get(clave, clave)


COLUMNAS_CANONICAS = {
    "fecha": "periodo",
    "periodo": "periodo",
    "mes": "periodo",
    "fechacorte": "periodo",
    "municipio": "municipio",
    "ciudad": "municipio",
    "segmento": "segmento",
    "segmentocliente": "segmento",
    "tipocliente": "segmento",
    "tipocompra": "tipo_compra",
    "modalidad": "tipo_compra",
    "compra": "tipo_compra",
    "energia": "energia",
    "energiakwh": "energia",
    "consumokwh": "energia",
    "kwh": "energia",
    "unidad": "unidad",
    "unidades": "unidad",
    "valorcop": "valor_cop",
    "valor": "valor_cop",
    "facturado": "valor_cop",
    "totalfacturadocop": "valor_cop",
    "clientes": "clientes",
    "numclientes": "clientes",
    "usuarios": "clientes",
    "clientesactivos": "clientes",
}
COLUMNAS_REQUERIDAS = {
    "periodo", "municipio", "segmento", "tipo_compra", "energia", "valor_cop", "clientes"
}
MESES = {
    "ene": 1, "enero": 1, "jan": 1, "january": 1,
    "feb": 2, "febrero": 2, "february": 2,
    "mar": 3, "marzo": 3, "march": 3,
    "abr": 4, "abril": 4, "apr": 4, "april": 4,
    "may": 5, "mayo": 5,
    "jun": 6, "junio": 6, "june": 6,
    "jul": 7, "julio": 7, "july": 7,
    "ago": 8, "agosto": 8, "aug": 8, "august": 8,
    "sep": 9, "set": 9, "sept": 9, "septiembre": 9, "setiembre": 9, "september": 9,
    "oct": 10, "octubre": 10, "october": 10,
    "nov": 11, "noviembre": 11, "november": 11,
    "dic": 12, "diciembre": 12, "dec": 12, "december": 12,
}


def _clave_encabezado(valor: object) -> str:
    if pd.isna(valor):
        return ""
    return re.sub(r"[^a-z0-9]", "", sin_tildes(str(valor)))


def _periodo_mensual(valor: object) -> str | None:
    if pd.isna(valor):
        return None
    texto = str(valor).strip().lower()
    if texto in {"", "total"}:
        return None
    if re.fullmatch(r"\d{4}-\d{1,2}", texto):
        anio, mes = map(int, texto.split("-"))
    elif re.fullmatch(r"\d{1,2}/\d{4}", texto):
        mes, anio = map(int, texto.split("/"))
    elif re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", texto):
        try:
            fecha = datetime.strptime(texto, "%d/%m/%Y")
        except ValueError:
            return None
        anio, mes = fecha.year, fecha.month
    elif re.fullmatch(r"[a-záéíóúñ]+-\d{2}", texto):
        nombre_mes, anio_corto = texto.split("-")
        mes = MESES.get(sin_tildes(nombre_mes))
        anio = 2000 + int(anio_corto)
        if mes is None:
            return None
    else:
        return None
    if mes < 1 or mes > 12:
        return None
    return f"{anio:04d}-{mes:02d}"


def _normalizar_numero(serie: pd.Series) -> pd.Series:
    texto = serie.astype("string").str.strip().str.replace(",", "", regex=False)
    texto = texto.mask(texto.eq(""))
    return pd.to_numeric(texto, errors="coerce")


def limpiar(bronce: pd.DataFrame, anio: int = 2023) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Normaliza una hoja de ventas mensual y separa filas irrecuperables."""
    fuente = bronce.drop(columns=LINAJE, errors="ignore")
    metricas: list[dict] = []

    def medir(problema: str, regla: str, antes: int | float, despues: int | float) -> None:
        metricas.append({
            "anio": anio,
            "problema": problema,
            "regla aplicada": regla,
            "antes": antes,
            "despues": despues,
        })

    fila_encabezado = None
    mapeo: dict[str, int] = {}
    for posicion_fila in range(len(fuente)):
        fila = fuente.iloc[posicion_fila]
        candidatos: dict[str, int] = {}
        for posicion, valor in enumerate(fila.tolist()):
            canonica = COLUMNAS_CANONICAS.get(_clave_encabezado(valor))
            if canonica and canonica not in candidatos:
                candidatos[canonica] = posicion
        if COLUMNAS_REQUERIDAS.issubset(candidatos):
            fila_encabezado = posicion_fila
            mapeo = candidatos
            break
    if fila_encabezado is None:
        raise ValueError(f"No se encontró un encabezado de ventas válido para {anio}.")

    columnas = ["periodo", "municipio", "segmento", "tipo_compra", "energia", "valor_cop", "clientes"]
    if "unidad" in mapeo:
        columnas.append("unidad")
    datos = pd.DataFrame({
        columna: fuente.iloc[fila_encabezado + 1:, mapeo[columna]].to_numpy()
        for columna in columnas
    })
    medir("Títulos y notas antes del encabezado", "Localizar encabezado y excluir preámbulo",
          int(fila_encabezado), 0)
    medir("Encabezado guardado como fila", "Usarlo como nombres de columna", 1, 0)

    total = datos["periodo"].astype("string").str.strip().str.upper().eq("TOTAL").fillna(False)
    medir("Filas de totales", "Excluir filas TOTAL", int(total.sum()), 0)
    datos = datos.loc[~total].copy()

    vacias = datos.isna().all(axis=1) | datos.astype("string").apply(
        lambda columna: columna.str.strip().eq("").fillna(True)
    ).all(axis=1)
    medir("Filas vacías", "Excluir filas sin ningún dato", int(vacias.sum()), 0)
    datos = datos.loc[~vacias].copy()

    duplicadas = datos.duplicated(keep="first")
    medir("Filas duplicadas exactas", "Conservar una sola copia",
          int(duplicadas.sum()), 0)
    datos = datos.loc[~duplicadas].copy()

    formatos = {
        "AAAA-MM": datos["periodo"].astype("string").str.fullmatch(r"\d{4}-\d{1,2}", na=False),
        "mes-AAAA corto": datos["periodo"].astype("string").str.fullmatch(r"[A-Za-záéíóúñÁÉÍÓÚÑ]+-\d{2}", na=False),
        "MM/AAAA": datos["periodo"].astype("string").str.fullmatch(r"\d{1,2}/\d{4}", na=False),
        "DD/MM/AAAA": datos["periodo"].astype("string").str.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", na=False),
    }
    datos["periodo"] = datos["periodo"].map(_periodo_mensual)
    medir("Formatos de fecha", "Normalizar fechas a AAAA-MM",
          int(sum(mask.sum() for mask in formatos.values())),
          int(datos["periodo"].notna().sum()))

    municipio_original = datos["municipio"].copy()
    claves_municipio = municipio_original.map(clave_municipio)
    municipio_valido = claves_municipio.isin(MUNICIPIOS)
    datos["divipola"] = claves_municipio.map(
        lambda clave: MUNICIPIOS[clave][0] if clave in MUNICIPIOS else None
    )
    datos["municipio"] = claves_municipio.map(
        lambda clave: MUNICIPIOS[clave][1] if clave in MUNICIPIOS else None
    )
    medir("Municipios con alias, tildes o errores", "Normalizar a nombre oficial y DIVIPOLA",
          int(municipio_original.nunique(dropna=True)),
          int(datos["municipio"].nunique(dropna=True)))

    segmento_original = datos["segmento"].copy()
    segmento_vacio = segmento_original.isna() | segmento_original.astype("string").str.strip().eq("")
    segmento_normalizado = segmento_original.map(
        lambda valor: SEGMENTOS.get(sin_tildes(str(valor))) if pd.notna(valor) else None
    )
    segmento_desconocido = segmento_normalizado.isna() & ~segmento_vacio
    datos["segmento"] = segmento_normalizado
    datos.loc[segmento_vacio, "segmento"] = "No informado"
    medir("Segmentos no estandarizados", "Unificar categorías y marcar vacíos",
          int(segmento_original.nunique(dropna=True)),
          int(datos["segmento"].nunique(dropna=True)))
    medir("Segmentos vacíos", "Marcar como 'No informado'",
          int(segmento_vacio.sum()), 0)

    tipo_original = datos["tipo_compra"].copy()
    datos["tipo_compra"] = datos["tipo_compra"].map(
        lambda valor: TIPOS_COMPRA.get(sin_tildes(str(valor))) if pd.notna(valor) else None
    )
    medir("Tipos de compra no estandarizados", "Unificar a Bolsa o Contrato",
          int(tipo_original.nunique(dropna=True)),
          int(datos["tipo_compra"].nunique(dropna=True)))

    energia_original = datos["energia"].copy()
    energia = _normalizar_numero(energia_original)
    unidad = (
        datos["unidad"].astype("string").str.strip().str.upper()
        if "unidad" in datos
        else pd.Series("KWH", index=datos.index)
    )
    energia_mwh = unidad.eq("MWH").fillna(False)
    energia_kwh = unidad.eq("KWH").fillna(False)
    unidad_valida = energia_mwh | energia_kwh
    energia = energia.where(~energia_mwh, energia * 1000)
    datos["energia_kwh"] = energia
    medir("Energía expresada en MWh", "Convertir MWh a kWh (× 1.000)",
          int(energia_mwh.sum()), int(energia_mwh.sum()))

    valor_fuente = datos["valor_cop"].copy()
    clientes_fuente = datos["clientes"].copy()
    datos["valor_cop"] = _normalizar_numero(valor_fuente)
    datos["clientes"] = _normalizar_numero(clientes_fuente)
    motivos: dict[object, list[str]] = {indice: [] for indice in datos.index}

    def agregar_motivo(mascara: pd.Series, motivo: str) -> int:
        indices = datos.index[mascara.fillna(False)]
        for indice in indices:
            motivos[indice].append(motivo)
        return len(indices)

    fecha_invalida = datos["periodo"].isna()
    agregar_motivo(fecha_invalida, "fecha ausente o formato mensual no reconocido")
    municipio_invalido = ~municipio_valido
    agregar_motivo(municipio_invalido, "municipio vacío o sin equivalencia DIVIPOLA")
    segmento_invalido = segmento_desconocido
    agregar_motivo(segmento_invalido, "segmento no reconocido")
    tipo_invalido = datos["tipo_compra"].isna()
    agregar_motivo(tipo_invalido, "tipo de compra vacío o no reconocido")
    unidad_invalida = ~unidad_valida
    agregar_motivo(unidad_invalida, "unidad de energía vacía o no reconocida")

    energia_vacia = energia_original.isna() | energia_original.astype("string").str.strip().eq("")
    energia_no_numerica = ~energia_vacia & energia.isna()
    energia_negativa = energia.lt(0)
    agregar_motivo(energia_vacia, "energía vacía")
    agregar_motivo(energia_no_numerica, "energía no numérica")
    agregar_motivo(energia_negativa, "energía negativa")
    medir("Energía vacía, inválida o negativa", "Enviar fila a cuarentena",
          int((energia_vacia | energia_no_numerica | energia_negativa).sum()), 0)

    valor_vacio = valor_fuente.isna() | valor_fuente.astype("string").str.strip().eq("")
    valor_no_numerico = ~valor_vacio & datos["valor_cop"].isna()
    valor_negativo = datos["valor_cop"].lt(0)
    agregar_motivo(valor_no_numerico, "valor facturado no numérico")
    agregar_motivo(valor_negativo, "valor facturado negativo")
    medir("Valores COP vacíos", "Conservar como nulo sin inventar el importe",
          int(valor_vacio.sum()), int(valor_vacio.sum()))
    clientes_vacios = clientes_fuente.isna() | clientes_fuente.astype("string").str.strip().eq("")
    clientes_no_numericos = ~clientes_vacios & datos["clientes"].isna()
    clientes_invalidos = datos["clientes"].isna() | datos["clientes"].lt(0) | (
        datos["clientes"].notna() & datos["clientes"].mod(1).ne(0)
    )
    agregar_motivo(clientes_no_numericos, "número de clientes no numérico")
    agregar_motivo(clientes_invalidos, "número de clientes ausente, negativo o no entero")

    salida = datos[[
        "periodo", "divipola", "municipio", "segmento", "tipo_compra",
        "energia_kwh", "valor_cop", "clientes",
    ]].copy()
    salida["energia_kwh"] = salida["energia_kwh"].astype("float64")
    salida["valor_cop"] = salida["valor_cop"].astype("float64")
    salida["clientes"] = salida["clientes"].astype("Int64")
    validas = pd.Series(
        [not motivos[indice] for indice in datos.index],
        index=datos.index,
    )
    duplicadas_clave = salida.loc[validas].duplicated(
        subset=["periodo", "divipola", "segmento", "tipo_compra"],
        keep="first",
    )
    indices_duplicados = duplicadas_clave[duplicadas_clave].index
    for indice in indices_duplicados:
        motivos[indice].append("llave mensual duplicada con valores distintos")
    medir("Llaves mensuales duplicadas", "Conservar primera fila y enviar conflicto a cuarentena",
          len(indices_duplicados), 0)

    cuarentena_mask = pd.Series(
        [bool(motivos[indice]) for indice in datos.index],
        index=datos.index,
    )
    cuarentena = salida.loc[cuarentena_mask].copy()
    cuarentena["motivo_cuarentena"] = [
        "; ".join(motivos[indice]) for indice in cuarentena.index
    ]
    limpias = salida.loc[~cuarentena_mask].copy()
    limpias["clientes"] = limpias["clientes"].astype("int64")
    medir("Filas enviadas a cuarentena", "Conservar todas las filas no corregibles con motivo",
          int(cuarentena_mask.sum()), int(len(cuarentena)))
    medir("Filas limpias", "Validar esquema de ventas",
          len(datos), len(limpias))
    return limpias.reset_index(drop=True), cuarentena.reset_index(drop=True), metricas


def limpiar_anio(bronce: pd.DataFrame, anio: int) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Limpia una de las hojas anuales con las reglas comunes de ventas."""
    return limpiar(bronce, anio=anio)


# ---------------------------------------------------------------------------
# REPORTE DE CALIDAD
# ---------------------------------------------------------------------------
def escribir_reporte(metricas: list[dict], filas_bronce: int, filas_plata: int, filas_cuarentena: int) -> None:
    """Escribe docs/reporte_calidad.md con la tabla de metricas antes y despues."""
    lineas = [
        "# Reporte de calidad: ventas de EnerAndes (2023–2026)\n",
        f"- Filas en bronce: {filas_bronce:,}",
        f"- Filas en plata: {filas_plata:,}",
        f"- Filas en cuarentena: {filas_cuarentena:,}\n",
        "| Año | Problema | Regla aplicada | Antes | Después |",
        "|---:|---|---|---:|---:|",
    ]
    for metrica in metricas:
        lineas.append(
            f"| {metrica['anio']} | {metrica['problema']} | {metrica['regla aplicada']} "
            f"| {metrica['antes']} | {metrica['despues']} |"
        )
    config.DIR_DOCS.mkdir(parents=True, exist_ok=True)
    (config.DIR_DOCS / "reporte_calidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def _main_2023() -> None:
    # Lee el archivo Parquet de bronce y lo guarda en la tabla bronce
    bronce = pd.read_parquet(config.DIR_BRONZE / "enerandes_ventas_2023.parquet")
    # len(bronce) es el numero de filas; log lo muestra con la hora
    log(f"Bronce: {len(bronce):,} filas")
    # Llama a limpiar(); como devuelve tres cosas, se reciben en tres variables
    limpias, cuarentena, metricas = limpiar(bronce)

    # Revisa la tabla limpia con las reglas de pandera.
    # Si una regla falla, el programa se detiene aqui y no guarda nada;
    # lazy=True: revisa todo y muestra TODOS los errores juntos
    ESQUEMA_VENTAS.validate(limpias, lazy=True)
    # Si llego a esta linea, la tabla cumplio todas las reglas
    log("Validacion con pandera: OK")

    # Crea la carpeta data/silver/ si no existe
    config.DIR_SILVER.mkdir(parents=True, exist_ok=True)
    # .to_parquet guarda la tabla en un archivo Parquet;
    # index=False: no guarda la columna de numeros de fila
    limpias.to_parquet(config.DIR_SILVER / "enerandes_ventas.parquet", index=False)
    cuarentena.to_parquet(config.DIR_SILVER / "enerandes_cuarentena.parquet", index=False)
    # Escribe docs/reporte_calidad.md
    escribir_reporte(metricas, len(bronce), len(limpias), len(cuarentena))

    # Muestra la tabla de metricas en la terminal, alineada en columnas:
    # :<42 ocupa 42 espacios alineado a la izquierda; :>7 ocupa 7 alineado a la derecha
    print(f"   {'problema':<42}{'antes':>7}{'despues':>9}")
    # Una linea por cada regla
    for m in metricas:
        print(f"   {m['problema']:<42}{m['antes']:>7}{m['despues']:>9}")
    log(f"Plata: {len(limpias):,} filas limpias y {len(cuarentena)} en cuarentena")
    log("Reporte en docs/reporte_calidad.md")


def main() -> None:
    tablas_limpias = []
    tablas_cuarentena = []
    metricas_totales = []
    filas_bronce = 0
    for anio in range(2023, 2027):
        bronce = pd.read_parquet(config.DIR_BRONZE / f"enerandes_ventas_{anio}.parquet")
        limpias, cuarentena, metricas = limpiar_anio(bronce, anio)
        ESQUEMA_VENTAS.validate(limpias, lazy=True)
        log(f"{anio}: validación Pandera OK ({len(limpias):,} filas)")
        tablas_limpias.append(limpias)
        tablas_cuarentena.append(cuarentena)
        metricas_totales.extend(metricas)
        filas_bronce += len(bronce)

    limpias = pd.concat(tablas_limpias, ignore_index=True)
    cuarentena = pd.concat(tablas_cuarentena, ignore_index=True)
    ESQUEMA_VENTAS.validate(limpias, lazy=True)
    config.DIR_SILVER.mkdir(parents=True, exist_ok=True)
    limpias.to_parquet(config.DIR_SILVER / "enerandes_ventas.parquet", index=False)
    cuarentena.to_parquet(config.DIR_SILVER / "enerandes_cuarentena.parquet", index=False)
    escribir_reporte(metricas_totales, filas_bronce, len(limpias), len(cuarentena))

    print(f"   {'año':<8}{'problema':<42}{'antes':>7}{'después':>9}")
    for metrica in metricas_totales:
        print(
            f"   {metrica['anio']:<8}{metrica['problema']:<42}"
            f"{metrica['antes']:>7}{metrica['despues']:>9}"
        )
    log(f"Plata: {len(limpias):,} filas limpias y {len(cuarentena)} en cuarentena")
    log("Reporte en docs/reporte_calidad.md")


# __name__ vale "__main__" solo cuando se ejecuta este archivo
# (python -m src.silver.enerandes). Si otro archivo lo importa (las pruebas),
# main() no se ejecuta: solo se usan sus funciones
if __name__ == "__main__":
    main()
