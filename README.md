# Observatorio de Energía y Clima

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

El proyecto reúne información pública del mercado eléctrico colombiano y del clima, junto con datos internos de ventas. La actividad 2 agrega limpieza y validación de la capa plata y un esquema estrella en DuckDB/dbt para análisis de energía, mercado y clima.

## Integrantes

| Nombre | Usuario GitHub | Rol |
| --- | --- | --- |
| Andres Cuenta Personal | amdrez22 | Líder técnico / Data Engineer |
| Andres Mejia Pelaez | amdrez22IUD | Analytics Engineer |
|  |  | Data Quality Analyst |
|  |  | BI Analyst / Storyteller |

## Fuentes de datos

| Fuente | Acceso y contenido | Alcance configurado | Salida en bronce |
| --- | --- | --- | --- |
| [XM / Sinergox](https://github.com/EquipoAnaliticaXM/API_XM) | API REST JSON: precio de bolsa, demanda, embalses, generación por recurso, aportes de energía y listado de recursos | Desde 2024-01-01 hasta `FECHA_FIN`; granularidad horaria o diaria. `ListadoRecursos` se consulta en `/lists`. | `xm_precio_bolsa`, `xm_demanda`, `xm_embalses`, `xm_generacion_recurso`, `xm_aportes_energia`, `xm_listado_recursos` |
| [IDEAM – precipitación](https://www.datos.gov.co/resource/s54a-sgyg.json) | API Socrata; precipitación agregada por día y estación | Antioquia desde 2025-01-01; consultas por ventanas semanales | `ideam_precipitacion_diaria` |
| [IDEAM – temperatura](https://datos.gov.co/d/sbwg-7ju4) | Dataset `sbwg-7ju4`; observaciones de sensores de temperatura del aire a 2 m, resumidas en promedio, mínimo y máximo diarios por estación | Antioquia desde 2025-01-01; consultas por ventanas semanales | `ideam_temperatura_diaria` |
| [NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/daily/) | API pública de temperatura a 2 m, precipitación corregida y radiación solar | Diario desde 2024-01-01 para el punto de referencia de Medellín (6.2442, -75.5812), en UTC | `nasa_power_clima_diario` |
| [NOAA ONI](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt) | Archivo público de texto con el Oceanic Niño Index | Serie histórica disponible en la fuente | `noaa_oni` |
| EnerAndes | Excel interno, una hoja por año | Requiere el archivo local indicado abajo | `enerandes_ventas_2023` … `enerandes_ventas_2026` |

NASA POWER se integra porque no requiere credenciales y aporta radiación solar, una variable útil para contextualizar el potencial de generación renovable junto con clima y mercado eléctrico. Es una estimación de una grilla global para un punto, no una medición de una estación local, por lo que no se debe tratar como equivalente directo a IDEAM. El IDEAM advierte que sus observaciones crudas pueden contener errores; deben validarse antes de usos sensibles. En NASA POWER, el valor de relleno `-999` debe tratarse como faltante en los análisis posteriores.

## Estructura del proyecto

```text
consultas/       Consultas SQL de ejemplo para DuckDB
  oro/           Consultas de negocio sobre el esquema estrella
data/
  bronze/        Parquet descargados (no versionados)
  silver/        Tablas limpias y cuarentenas (no versionadas)
  observatorio.duckdb Base DuckDB de la capa oro (no versionada)
  insumos/       Archivo Excel de EnerAndes usado por el pipeline
  sample/        Muestras CSV pequeñas de fuentes públicas
dbt/
  models/
    staging/     Lectura de las tablas plata
    marts/       Dimensiones y hechos de la capa oro
src/
  extract/       Un extractor por fuente
  silver/        Limpieza de EnerAndes y demás fuentes
  quality/       Esquemas Pandera y reporte de calidad
  config.py      Fechas, URLs, parámetros y rutas centrales
  pipeline.py    Extracción de las fuentes a bronce
  transformar.py Construcción reproducible de plata y oro
  documentar_datos.py Exportación de muestras públicas y perfilamiento de bronce
  consultar.py   Ejecución de las consultas SQL
  perfilamiento.py Perfil reproducible de data/sample/
docs/            Reportes de calidad, perfilamiento y documentación dimensional
tests/           Pruebas automatizadas con pytest
```

La arquitectura implementada es `fuentes -> bronce -> plata -> oro -> análisis`. Bronce conserva el dato recibido y sus metadatos de linaje. Plata normaliza fechas, categorías, unidades y granularidad; valida las tablas con Pandera y preserva los datos no corregibles en cuarentena. Oro contiene el modelo dimensional creado por dbt y DuckDB. Los datos completos de `data/bronze/`, `data/silver/` y la base `.duckdb` se generan localmente y están excluidos de Git.

## Instalación y ejecución

Requiere Python y acceso a Internet para descargar las fuentes públicas.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno, permite scripts solo en la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

El archivo `ventas_enerandes_2023_2026.xlsx` se encuentra en `data/insumos/` y está incluido en el repositorio como insumo recreativo y educativo. Luego:

```powershell
python -m src.pipeline
python -m src.documentar_datos
python -m src.perfilamiento
python -m src.transformar
python -m src.consultar
python -m pytest
```

`python -m src.pipeline` crea o actualiza los archivos bronce y puede tardar varios minutos. Con esos datos disponibles, `python -m src.transformar` ejecuta la limpieza de EnerAndes, XM, IDEAM, NOAA y NASA POWER, valida las tablas con Pandera, actualiza el reporte de calidad y ejecuta `dbt build` para crear plata y oro. Es el comando único para reproducir las transformaciones; no descarga datos de Internet.

`src.documentar_datos` exporta a `data/sample/` las primeras 200 filas de cada Parquet disponible, incluidas las salidas de EnerAndes, y genera `docs/perfilamiento.md`. Vuelve a ejecutar este comando después de cada extracción para actualizar las muestras y el perfilamiento. El pipeline omite los Parquet existentes; para descargarlos de nuevo:

```powershell
python -m src.pipeline --forzar
```

El rango principal se configura en `src/config.py`. XM limita las consultas horarias y diarias a ventanas de hasta 30 días; IDEAM consulta y pagina ventanas semanales; el listado de recursos usa el endpoint `lists` sin fechas. NASA POWER consulta el intervalo completo de una vez. Las descargas de IDEAM y XM pueden tardar varios minutos.

## Muestras y perfilamiento

`docs/perfilamiento.md` contiene el perfil técnico de los Parquet públicos. `docs/reporte_calidad.md` registra las reglas aplicadas y las métricas antes/después de las transformaciones plata, incluyendo los motivos y conteos de cuarentena. `src.perfilamiento` resume muestras cortas; estas no permiten inferir tendencias anuales ni causalidad.

## Evidencia 2: calidad y modelo dimensional

La limpieza mensual de EnerAndes une las hojas 2023–2026. Convierte los formatos de fechas a `AAAA-MM`, interpreta las fechas completas de 2026 como día/mes/año, convierte MWh a kWh y normaliza municipios y categorías. Las demás fuentes convierten los valores y fechas a tipos nativos; XM horario queda en formato largo y NOAA asigna DJF a enero y calcula la fase ENSO. Cada esquema Pandera se valida antes de escribir plata.

El esquema oro contiene tres hechos:

| Hecho | Grano |
|---|---|
| `fact_ventas_mensual` | Mes, municipio, segmento y tipo de compra. |
| `fact_mercado_horario` | Fecha, hora y código de mercado. |
| `fact_generacion_recurso` | Fecha, hora y código de recurso/planta. |

Sus dimensiones son `dim_fecha`, `dim_mes`, `dim_hora`, `dim_municipio`, `dim_segmento` y `dim_recurso`. El [diagrama y los granos](docs/modelo_dimensional.md) y el [diccionario de datos](docs/diccionario_datos.md) describen las tablas y columnas.

### Resumen de calidad

Con los insumos bronce locales procesados en esta ejecución:

- EnerAndes: **4.184** filas recibidas; **4.007** filas limpias y **43** en cuarentena. Las filas en cuarentena tienen energía vacía o negativa; las filas exactas repetidas y las filas de total no se incorporan a plata.
- XM: las 24 horas por día se normalizaron en **8.456.856** filas para precio, demanda y generación. Las celdas vacías de generación permanecen como nulos; no se imputaron.
- `ListadoRecursos`: se conservaron **2.491** códigos únicos; dos registros duplicados exactos se consolidaron.
- IDEAM, NOAA ONI y NASA POWER se transformaron a sus esquemas plata validados con Pandera. Los **61** valores centinela `-999` de radiación NASA POWER se representan como faltantes.

El detalle medido por fuente se genera en [reporte_calidad.md](docs/reporte_calidad.md) al ejecutar `python -m src.transformar`.

### Consultas de negocio en oro

Las consultas están en [consultas/oro](consultas/oro) y se ejecutan junto con las consultas de bronce con `python -m src.consultar` después de construir oro.

**Energía, facturación y clientes reportados por año:**

| Año | Energía total (kWh) | Valor facturado (COP) | Clientes reportados |
|---:|---:|---:|---:|
| 2023 | 721.076.542 | 632.140.740.525 | 2.090.780 |
| 2024 | 736.644.762 | 704.851.180.051 | 2.092.393 |
| 2025 | 770.627.255 | 811.617.971.096 | 2.230.855 |
| 2026* | 595.266.845 | 675.627.970.398 | 1.734.300 |

Los clientes son sumas de los valores reportados en cada venta mensual, no un conteo de personas únicas. *2026 cubre los meses disponibles en los datos bronce.

**Precio y demanda promedio por fase ENSO (2024–2026):**

| Fase ENSO | Días | Precio promedio (COP/kWh) | Demanda promedio reportada |
|---|---:|---:|---:|
| El Niño | 244 | 661,30 | 9.753.759 |
| La Niña | 92 | 222,83 | 9.650.512 |
| Neutral | 668 | 425,65 | 9.516.068 |

**Cinco recursos con mayor generación acumulada reportada por XM:**

| Código | Recurso | Tipo | Generación reportada acumulada |
|---|---|---|---:|
| PES1 | ITUANGO | HIDRAULICA | 22.169.960.070,27 |
| SNCR | SAN CARLOS | HIDRAULICA | 16.795.075.358,31 |
| GVIO | GUAVIO | HIDRAULICA | 15.080.822.084,31 |
| SOG1 | SOGAMOSO | HIDRAULICA | 13.150.683.753,74 |
| CHVR | CHIVOR | HIDRAULICA | 9.795.368.502,08 |

La columna de generación conserva la unidad tal como la entrega XM; el resultado es una suma, no una conversión de unidades.

### Videos de sustentación EA2

| Integrante | Enlace |
|---|---|
| Andres Cuenta Personal | Pendiente |
| Andres Mejia Pelaez | Pendiente |
| Data Quality Analyst | Pendiente |
| BI Analyst / Storyteller | Pendiente |

## Pruebas

Las pruebas no necesitan descargar datos ni conectarse a las APIs:

```powershell
python -m pytest
```

Cubren el aplanamiento de las respuestas de XM y NASA POWER, consultas a IDEAM, el flujo de extracción y la salida del perfilamiento.

## Entregables colaborativos

Cada integrante debe registrar al menos tres commits propios, abrir al menos un PR propio, completar su bitácora y entregar un video individual de máximo cinco minutos. Estos elementos los completa cada integrante; los commits y PR de una persona no sustituyen los de los demás.

La bitácora individual de Andrés Mejía Peláez está en [docs/bitacoras/Mejia_Andres.md](docs/bitacoras/Mejia_Andres.md).

### Sustentación de la actividad 1

[Ver el video de sustentación](https://drive.google.com/file/d/1nc-ePc2dakYezfVAF5iRt7wP4uL8f6E9/view?usp=sharing).

Para la entrega de la actividad 2, crear y publicar la etiqueta acordada:

```powershell
git tag ea2
git push origin ea2
```

## Uso de IA

Se utilizó GitHub Copilot como apoyo para implementar y revisar extractores, pruebas y documentación. El equipo debe revisar los cambios, validar las fuentes y declarar el uso de IA de acuerdo con las reglas de la asignatura.
