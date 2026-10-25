# Perfilamiento de la capa bronce

Generado: 2026-10-25T15:34-05:00.

Este reporte describe los Parquet encontrados en `data/bronze/` en el momento de su generación. Vuelva a generarlo después de ejecutar `python -m src.pipeline` para reflejar la extracción completa.

El archivo de EnerAndes usado en esta actividad es recreativo y educativo; se incluyen sus Parquet y muestras de hasta 200 filas.

## Hallazgos de calidad

1. El perfil cubre 14 archivos presentes, 410,131 filas y 11,227,823 celdas.
2. Se encontraron 148 valores nulos explícitos (0.0013% de las celdas perfiladas).
3. Se encontraron 122 filas duplicadas completas en los 410,131 registros perfilados.
4. En las series horarias XM hay 2,473,215 cadenas vacías (29.25%) y 0 valores no numéricos no vacíos, entre 8,456,856 celdas.
5. NASA POWER contiene 61 valores de relleno `-999`.
6. Faltan localmente 0 archivos configurados para perfilar: ninguno.
7. Archivos cuya fecha mínima no alcanza el inicio configurado: ninguno.

## Archivos presentes

### `enerandes_ventas_2023.parquet`

- Filas: **1,114**
- Columnas: **10**
- Filas duplicadas completas: **32**
- Rango de fechas: No identificable en las columnas

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `col_0` | `str` | 0 | 0.00% |
| `col_1` | `str` | 1 | 0.09% |
| `col_2` | `str` | 16 | 1.44% |
| `col_3` | `str` | 1 | 0.09% |
| `col_4` | `str` | 10 | 0.90% |
| `col_5` | `str` | 8 | 0.72% |
| `col_6` | `str` | 1 | 0.09% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `enerandes_ventas_2024.parquet`

- Filas: **1,114**
- Columnas: **11**
- Filas duplicadas completas: **32**
- Rango de fechas: No identificable en las columnas

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `col_0` | `str` | 0 | 0.00% |
| `col_1` | `str` | 1 | 0.09% |
| `col_2` | `str` | 4 | 0.36% |
| `col_3` | `str` | 1 | 0.09% |
| `col_4` | `str` | 8 | 0.72% |
| `col_5` | `str` | 1 | 0.09% |
| `col_6` | `str` | 12 | 1.08% |
| `col_7` | `str` | 1 | 0.09% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `enerandes_ventas_2025.parquet`

- Filas: **1,117**
- Columnas: **10**
- Filas duplicadas completas: **32**
- Rango de fechas: No identificable en las columnas

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `col_0` | `str` | 1 | 0.09% |
| `col_1` | `str` | 4 | 0.36% |
| `col_2` | `str` | 10 | 0.90% |
| `col_3` | `str` | 4 | 0.36% |
| `col_4` | `str` | 10 | 0.90% |
| `col_5` | `str` | 8 | 0.72% |
| `col_6` | `str` | 4 | 0.36% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `enerandes_ventas_2026.parquet`

- Filas: **839**
- Columnas: **10**
- Filas duplicadas completas: **24**
- Rango de fechas: No identificable en las columnas

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `col_0` | `str` | 1 | 0.12% |
| `col_1` | `str` | 4 | 0.48% |
| `col_2` | `str` | 9 | 1.07% |
| `col_3` | `str` | 4 | 0.48% |
| `col_4` | `str` | 9 | 1.07% |
| `col_5` | `str` | 11 | 1.31% |
| `col_6` | `str` | 4 | 0.48% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `ideam_precipitacion_diaria.parquet`

- Filas: **29,804**
- Columnas: **11**
- Filas duplicadas completas: **0**
- Rango de fechas: fecha: 2025-01-01 a 2026-07-24

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `codigoestacion` | `str` | 0 | 0.00% |
| `nombreestacion` | `str` | 0 | 0.00% |
| `municipio` | `str` | 0 | 0.00% |
| `latitud` | `str` | 0 | 0.00% |
| `longitud` | `str` | 0 | 0.00% |
| `fecha` | `str` | 0 | 0.00% |
| `precipitacion_mm` | `str` | 0 | 0.00% |
| `n_obs` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `ideam_temperatura_diaria.parquet`

- Filas: **17,349**
- Columnas: **13**
- Filas duplicadas completas: **0**
- Rango de fechas: fecha: 2025-01-01 a 2026-07-24

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `codigoestacion` | `str` | 0 | 0.00% |
| `nombreestacion` | `str` | 0 | 0.00% |
| `municipio` | `str` | 0 | 0.00% |
| `latitud` | `str` | 0 | 0.00% |
| `longitud` | `str` | 0 | 0.00% |
| `fecha` | `str` | 0 | 0.00% |
| `temperatura_promedio_c` | `str` | 0 | 0.00% |
| `temperatura_minima_c` | `str` | 0 | 0.00% |
| `temperatura_maxima_c` | `str` | 0 | 0.00% |
| `n_obs` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `nasa_power_clima_diario.parquet`

- Filas: **1,004**
- Columnas: **7**
- Filas duplicadas completas: **0**
- Rango de fechas: fecha: 2024-01-01 a 2026-09-30

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `fecha` | `str` | 0 | 0.00% |
| `temperatura_2m_c` | `float64` | 0 | 0.00% |
| `precipitacion_corregida_mm_dia` | `float64` | 0 | 0.00% |
| `radiacion_solar_kwh_m2_dia` | `float64` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `noaa_oni.parquet`

- Filas: **920**
- Columnas: **7**
- Filas duplicadas completas: **0**
- Rango de fechas: YR: 1950-01-01 a 2026-01-01

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `SEAS` | `str` | 0 | 0.00% |
| `YR` | `str` | 0 | 0.00% |
| `TOTAL` | `str` | 0 | 0.00% |
| `ANOM` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `xm_aportes_energia.parquet`

- Filas: **1,004**
- Columnas: **6**
- Filas duplicadas completas: **0**
- Rango de fechas: Date: 2024-01-01 a 2026-09-30

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `Date` | `str` | 0 | 0.00% |
| `Id` | `str` | 0 | 0.00% |
| `Value` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `xm_demanda.parquet`

- Filas: **1,004**
- Columnas: **30**
- Filas duplicadas completas: **0**
- Rango de fechas: Date: 2024-01-01 a 2026-09-30

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `Date` | `str` | 0 | 0.00% |
| `Id` | `str` | 0 | 0.00% |
| `code` | `str` | 0 | 0.00% |
| `Hour01` | `str` | 0 | 0.00% |
| `Hour02` | `str` | 0 | 0.00% |
| `Hour03` | `str` | 0 | 0.00% |
| `Hour04` | `str` | 0 | 0.00% |
| `Hour05` | `str` | 0 | 0.00% |
| `Hour06` | `str` | 0 | 0.00% |
| `Hour07` | `str` | 0 | 0.00% |
| `Hour08` | `str` | 0 | 0.00% |
| `Hour09` | `str` | 0 | 0.00% |
| `Hour10` | `str` | 0 | 0.00% |
| `Hour11` | `str` | 0 | 0.00% |
| `Hour12` | `str` | 0 | 0.00% |
| `Hour13` | `str` | 0 | 0.00% |
| `Hour14` | `str` | 0 | 0.00% |
| `Hour15` | `str` | 0 | 0.00% |
| `Hour16` | `str` | 0 | 0.00% |
| `Hour17` | `str` | 0 | 0.00% |
| `Hour18` | `str` | 0 | 0.00% |
| `Hour19` | `str` | 0 | 0.00% |
| `Hour20` | `str` | 0 | 0.00% |
| `Hour21` | `str` | 0 | 0.00% |
| `Hour22` | `str` | 0 | 0.00% |
| `Hour23` | `str` | 0 | 0.00% |
| `Hour24` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `xm_embalses.parquet`

- Filas: **1,004**
- Columnas: **6**
- Filas duplicadas completas: **0**
- Rango de fechas: Date: 2024-01-01 a 2026-09-30

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `Date` | `str` | 0 | 0.00% |
| `Id` | `str` | 0 | 0.00% |
| `Value` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `xm_generacion_recurso.parquet`

- Filas: **350,361**
- Columnas: **30**
- Filas duplicadas completas: **0**
- Rango de fechas: Date: 2024-01-01 a 2026-09-30

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `Date` | `str` | 0 | 0.00% |
| `Id` | `str` | 0 | 0.00% |
| `code` | `str` | 0 | 0.00% |
| `Hour01` | `str` | 0 | 0.00% |
| `Hour02` | `str` | 0 | 0.00% |
| `Hour03` | `str` | 0 | 0.00% |
| `Hour04` | `str` | 0 | 0.00% |
| `Hour05` | `str` | 0 | 0.00% |
| `Hour06` | `str` | 0 | 0.00% |
| `Hour07` | `str` | 0 | 0.00% |
| `Hour08` | `str` | 0 | 0.00% |
| `Hour09` | `str` | 0 | 0.00% |
| `Hour10` | `str` | 0 | 0.00% |
| `Hour11` | `str` | 0 | 0.00% |
| `Hour12` | `str` | 0 | 0.00% |
| `Hour13` | `str` | 0 | 0.00% |
| `Hour14` | `str` | 0 | 0.00% |
| `Hour15` | `str` | 0 | 0.00% |
| `Hour16` | `str` | 0 | 0.00% |
| `Hour17` | `str` | 0 | 0.00% |
| `Hour18` | `str` | 0 | 0.00% |
| `Hour19` | `str` | 0 | 0.00% |
| `Hour20` | `str` | 0 | 0.00% |
| `Hour21` | `str` | 0 | 0.00% |
| `Hour22` | `str` | 0 | 0.00% |
| `Hour23` | `str` | 0 | 0.00% |
| `Hour24` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `xm_listado_recursos.parquet`

- Filas: **2,493**
- Columnas: **14**
- Filas duplicadas completas: **2**
- Rango de fechas: Date: 2026-10-25 a 2026-10-25

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `Date` | `str` | 0 | 0.00% |
| `Id` | `str` | 0 | 0.00% |
| `Code` | `str` | 0 | 0.00% |
| `Name` | `str` | 0 | 0.00% |
| `Type` | `str` | 0 | 0.00% |
| `Disp` | `str` | 0 | 0.00% |
| `RecType` | `str` | 0 | 0.00% |
| `CompanyCode` | `str` | 0 | 0.00% |
| `EnerSource` | `str` | 0 | 0.00% |
| `OperStartdate` | `str` | 0 | 0.00% |
| `State` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

### `xm_precio_bolsa.parquet`

- Filas: **1,004**
- Columnas: **30**
- Filas duplicadas completas: **0**
- Rango de fechas: Date: 2024-01-01 a 2026-09-30

| Columna | Tipo | Nulos | Nulos (%) |
| --- | --- | ---: | ---: |
| `Date` | `str` | 0 | 0.00% |
| `Id` | `str` | 0 | 0.00% |
| `code` | `str` | 0 | 0.00% |
| `Hour01` | `str` | 0 | 0.00% |
| `Hour02` | `str` | 0 | 0.00% |
| `Hour03` | `str` | 0 | 0.00% |
| `Hour04` | `str` | 0 | 0.00% |
| `Hour05` | `str` | 0 | 0.00% |
| `Hour06` | `str` | 0 | 0.00% |
| `Hour07` | `str` | 0 | 0.00% |
| `Hour08` | `str` | 0 | 0.00% |
| `Hour09` | `str` | 0 | 0.00% |
| `Hour10` | `str` | 0 | 0.00% |
| `Hour11` | `str` | 0 | 0.00% |
| `Hour12` | `str` | 0 | 0.00% |
| `Hour13` | `str` | 0 | 0.00% |
| `Hour14` | `str` | 0 | 0.00% |
| `Hour15` | `str` | 0 | 0.00% |
| `Hour16` | `str` | 0 | 0.00% |
| `Hour17` | `str` | 0 | 0.00% |
| `Hour18` | `str` | 0 | 0.00% |
| `Hour19` | `str` | 0 | 0.00% |
| `Hour20` | `str` | 0 | 0.00% |
| `Hour21` | `str` | 0 | 0.00% |
| `Hour22` | `str` | 0 | 0.00% |
| `Hour23` | `str` | 0 | 0.00% |
| `Hour24` | `str` | 0 | 0.00% |
| `_fuente` | `str` | 0 | 0.00% |
| `_origen` | `str` | 0 | 0.00% |
| `_extraido_en` | `str` | 0 | 0.00% |

## Archivos esperados no encontrados

Todos los archivos esperados están disponibles.
