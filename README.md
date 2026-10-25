# Observatorio de Energía y Clima

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

El proyecto reúne información pública del mercado eléctrico colombiano y del clima, junto con datos internos de ventas, para facilitar análisis exploratorios de riesgo energético y del fenómeno El Niño. La extracción actual implementa la capa bronce; las capas plata y oro son parte de la arquitectura objetivo, no de los procesos de este repositorio.

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
data/
  bronze/        Parquet descargados (no versionados)
  insumos/       Archivo Excel de EnerAndes usado por el pipeline
  sample/        Muestras CSV pequeñas de fuentes públicas
src/
  extract/       Un extractor por fuente
  config.py      Fechas, URLs, parámetros y rutas centrales
  pipeline.py    Punto de entrada de las extracciones
  documentar_datos.py Exportación de muestras públicas y perfilamiento de bronce
  consultar.py   Ejecución de las consultas SQL
  perfilamiento.py Perfil reproducible de data/sample/
docs/            Perfilamiento técnico de la capa bronce
tests/           Pruebas automatizadas con pytest
```

La arquitectura objetivo es `fuentes -> bronce -> plata -> oro -> análisis`. En bronce se conserva el dato descargado y se añaden `_fuente`, `_origen` y `_extraido_en` como metadatos de linaje. Los archivos completos de `data/bronze/` se generan localmente y se excluyen de Git; los CSV de `data/sample/` son ejemplos reducidos y versionados. El Excel de EnerAndes usado en esta actividad es recreativo y educativo, y se conserva junto con una muestra de sus salidas.

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
python -m src.consultar
python -m src.perfilamiento
python -m pytest
```

`src.documentar_datos` exporta a `data/sample/` las primeras 200 filas de cada Parquet disponible, incluidas las salidas de EnerAndes, y genera `docs/perfilamiento.md`. Vuelve a ejecutar este comando después de cada extracción para actualizar las muestras y el perfilamiento. El pipeline omite los Parquet existentes; para descargarlos de nuevo:

```powershell
python -m src.pipeline --forzar
```

El rango principal se configura en `src/config.py`. XM limita las consultas horarias y diarias a ventanas de hasta 30 días; IDEAM consulta y pagina ventanas semanales; el listado de recursos usa el endpoint `lists` sin fechas. NASA POWER consulta el intervalo completo de una vez. Las descargas de IDEAM y XM pueden tardar varios minutos.

## Muestras y perfilamiento

`docs/perfilamiento.md` contiene el perfil técnico de cada Parquet público disponible y al menos cinco verificaciones de calidad con evidencia numérica. `src.perfilamiento` resume las muestras; al ser muestras cortas y de fechas/ubicaciones limitadas, no permiten inferir tendencias anuales, causalidad ni relaciones estadísticas entre fuentes. Para esos análisis se deben usar los Parquet completos, validar calidad y alinear fechas, zonas horarias, unidades y granularidades.

## Pruebas

Las pruebas no necesitan descargar datos ni conectarse a las APIs:

```powershell
python -m pytest
```

Cubren el aplanamiento de las respuestas de XM y NASA POWER, consultas a IDEAM, el flujo de extracción y la salida del perfilamiento.

## Entregables colaborativos

Cada integrante debe registrar al menos tres commits propios, abrir al menos un PR propio, completar su bitácora y entregar un video individual de máximo cinco minutos. Estos elementos los completa cada integrante; los commits y PR de una persona no sustituyen los de los demás.

### Sustentación de la actividad 1

[Ver el video de sustentación](https://drive.google.com/file/d/1nc-ePc2dakYezfVAF5iRt7wP4uL8f6E9/view?usp=sharing).

Para la entrega final, crear y publicar la etiqueta acordada:

```powershell
git tag ea1
git push origin ea1
```

## Uso de IA

Se utilizó GitHub Copilot como apoyo para implementar y revisar extractores, pruebas y documentación. El equipo debe revisar los cambios, validar las fuentes y declarar el uso de IA de acuerdo con las reglas de la asignatura.
