# Diccionario de datos de la capa oro

Los tipos corresponden a DuckDB después de ejecutar `dbt build`.

## `dim_mes`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `mes_id` | INTEGER | Llave numérica AAAAMM. | Periodo de EnerAndes. |
| `periodo` | VARCHAR | Mes en formato AAAA-MM. | `enerandes_ventas.periodo`. |
| `anio` | INTEGER | Año del periodo. | Derivado de `periodo`. |
| `mes` | INTEGER | Mes del año, de 1 a 12. | Derivado de `periodo`. |
| `trimestre` | INTEGER | Trimestre calendario, de 1 a 4. | Derivado de `mes`. |

## `dim_fecha`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `fecha_id` | INTEGER | Llave numérica AAAAMMDD. | Fecha diaria generada por dbt. |
| `fecha` | DATE | Día calendario. | Rango de fechas de las fuentes plata. |
| `anio` | INTEGER | Año calendario. | Derivado de `fecha`. |
| `mes` | INTEGER | Mes calendario, de 1 a 12. | Derivado de `fecha`. |
| `trimestre` | INTEGER | Trimestre calendario. | Derivado de `fecha`. |
| `dia` | INTEGER | Día del mes. | Derivado de `fecha`. |
| `dia_semana_num` | INTEGER | Día ISO de semana, de 1 a 7. | Derivado de `fecha`. |
| `dia_semana` | VARCHAR | Nombre del día de semana. | Derivado de `fecha`. |
| `fase_enso` | VARCHAR | El Niño, La Niña o Neutral para el mes. | `noaa_oni_mensual.fase_enso`; Neutral si no hay registro. |

## `dim_hora`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `hora_id` | BIGINT | Llave de hora, de 1 a 24. | Serie generada por dbt. |
| `hora` | BIGINT | Número de hora XM. | Serie generada por dbt. |
| `hora_inicio` | VARCHAR | Etiqueta HH:00 para la hora. | Derivada de `hora`. |
| `franja_horaria` | VARCHAR | Madrugada, mañana, tarde o noche. | Derivada de `hora`. |

## `dim_municipio`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `municipio_id` | VARCHAR | Código DIVIPOLA de cinco dígitos. | `enerandes_ventas.divipola`. |
| `municipio` | VARCHAR | Nombre oficial normalizado. | `enerandes_ventas.municipio`. |

## `dim_segmento`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `segmento_id` | BIGINT | Llave sustituta del segmento. | Numeración determinista de dbt. |
| `segmento` | VARCHAR | Residencial, Comercial, Industrial o No informado. | `enerandes_ventas.segmento`. |

## `dim_recurso`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `codigo_recurso` | VARCHAR | Código único del recurso XM. | `xm_listado_recursos.codigo_recurso` y generación histórica. |
| `nombre_recurso` | VARCHAR | Nombre de planta o recurso. | Catálogo XM; código para recursos sin catálogo. |
| `tipo` | VARCHAR | Tipo de tecnología. | Catálogo XM; “Sin información” si falta. |
| `disponibilidad` | VARCHAR | Clasificación de despacho. | Catálogo XM. |
| `tipo_recurso` | VARCHAR | Tipo operativo del recurso. | Catálogo XM. |
| `codigo_empresa` | VARCHAR | Código de empresa propietaria. | Catálogo XM. |
| `fuente_energia` | VARCHAR | Fuente energética declarada. | Catálogo XM. |
| `fecha_inicio_operacion` | DATE | Inicio de operación reportado. | Catálogo XM. |
| `estado` | VARCHAR | Estado del recurso. | Catálogo XM. |
| `en_catalogo` | BOOLEAN | Indica si el código existe en el catálogo actual. | Derivado del cruce con generación. |

## `fact_ventas_mensual`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `mes_id` | INTEGER | Llave a `dim_mes`. | `enerandes_ventas.periodo`. |
| `fecha_id` | INTEGER | Llave al primer día del mes en `dim_fecha`. | `enerandes_ventas.periodo`. |
| `municipio_id` | VARCHAR | Llave DIVIPOLA a `dim_municipio`. | `enerandes_ventas.divipola`. |
| `segmento_id` | BIGINT | Llave a `dim_segmento`. | Cruce de `enerandes_ventas.segmento`. |
| `tipo_compra` | VARCHAR | Bolsa o Contrato. | `enerandes_ventas.tipo_compra`. |
| `energia_kwh` | DOUBLE | Energía vendida en kWh. | `enerandes_ventas.energia_kwh`. |
| `valor_cop` | DOUBLE | Valor facturado en pesos colombianos. | `enerandes_ventas.valor_cop`. |
| `clientes` | BIGINT | Clientes reportados. | `enerandes_ventas.clientes`. |

## `fact_mercado_horario`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `fecha_id` | INTEGER | Llave a `dim_fecha`. | Fecha de XM. |
| `hora_id` | BIGINT | Llave a `dim_hora`, de 1 a 24. | Hora de XM. |
| `codigo_mercado` | VARCHAR | Código del sistema o entidad de mercado. | XM precio/demanda `codigo`. |
| `precio_bolsa` | DOUBLE | Precio de bolsa en la hora. | `xm_precio_bolsa_horario.precio_bolsa`. |
| `demanda` | DOUBLE | Demanda reportada en la hora. | `xm_demanda_horaria.demanda`. |

## `fact_generacion_recurso`

| Columna | Tipo | Descripción | Origen |
|---|---|---|---|
| `fecha_id` | INTEGER | Llave a `dim_fecha`. | Fecha de XM. |
| `hora_id` | BIGINT | Llave a `dim_hora`, de 1 a 24. | Hora de XM. |
| `codigo_recurso` | VARCHAR | Llave a `dim_recurso`. | `xm_generacion_recurso_horaria.codigo_recurso`. |
| `generacion` | DOUBLE | Generación reportada por XM para el recurso y hora. | `xm_generacion_recurso_horaria.generacion`. |
