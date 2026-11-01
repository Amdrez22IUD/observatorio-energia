# Reporte de calidad de la capa plata

Las métricas se generan al ejecutar `python -m src.transformar`. Cada regla muestra el conteo antes y después; los datos no corregibles se conservan en su archivo de cuarentena.

| Fuente/tabla | Filas recibidas | Filas plata | Filas en cuarentena |
|---|---:|---:|---:|
| EnerAndes | 4,184 | 4,007 | 43 |
| ideam_precipitacion_diaria | 29,804 | 29,804 | 0 |
| ideam_temperatura_diaria | 17,349 | 17,349 | 0 |
| nasa_power_clima_diario | 1,004 | 1,004 | 0 |
| noaa_oni_mensual | 920 | 920 | 0 |
| xm_aportes_energia_diarios | 1,004 | 1,004 | 0 |
| xm_demanda_horaria | 1,004 | 24,096 | 0 |
| xm_embalses_diarios | 1,004 | 1,004 | 0 |
| xm_generacion_recurso_horaria | 350,361 | 8,408,664 | 0 |
| xm_listado_recursos | 2,493 | 2,491 | 0 |
| xm_precio_bolsa_horario | 1,004 | 24,096 | 0 |

## EnerAndes

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| 2023 | Títulos y notas antes del encabezado | Localizar encabezado y excluir preámbulo | 0 | 0 |
| 2023 | Encabezado guardado como fila | Usarlo como nombres de columna | 1 | 0 |
| 2023 | Filas de totales | Excluir filas TOTAL | 1 | 0 |
| 2023 | Filas vacías | Excluir filas sin ningún dato | 0 | 0 |
| 2023 | Filas duplicadas exactas | Conservar una sola copia | 32 | 0 |
| 2023 | Formatos de fecha | Normalizar fechas a AAAA-MM | 1,080 | 1,080 |
| 2023 | Municipios con alias, tildes o errores | Normalizar a nombre oficial y DIVIPOLA | 31 | 15 |
| 2023 | Segmentos no estandarizados | Unificar categorías y marcar vacíos | 6 | 4 |
| 2023 | Segmentos vacíos | Marcar como 'No informado' | 14 | 0 |
| 2023 | Tipos de compra no estandarizados | Unificar a Bolsa o Contrato | 4 | 2 |
| 2023 | Energía expresada en MWh | Convertir MWh a kWh (× 1.000) | 0 | 0 |
| 2023 | Energía vacía, inválida o negativa | Enviar fila a cuarentena | 16 | 0 |
| 2023 | Valores COP vacíos | Conservar como nulo sin inventar el importe | 7 | 7 |
| 2023 | Llaves mensuales duplicadas | Conservar primera fila y enviar conflicto a cuarentena | 0 | 0 |
| 2023 | Filas enviadas a cuarentena | Conservar todas las filas no corregibles con motivo | 16 | 16 |
| 2023 | Filas limpias | Validar esquema de ventas | 1,080 | 1,064 |
| 2023 | Filas de bronce recibidas | Detectar encabezado, preámbulo y filas de datos | 1,114 | 1,114 |
| 2024 | Títulos y notas antes del encabezado | Localizar encabezado y excluir preámbulo | 0 | 0 |
| 2024 | Encabezado guardado como fila | Usarlo como nombres de columna | 1 | 0 |
| 2024 | Filas de totales | Excluir filas TOTAL | 1 | 0 |
| 2024 | Filas vacías | Excluir filas sin ningún dato | 0 | 0 |
| 2024 | Filas duplicadas exactas | Conservar una sola copia | 32 | 0 |
| 2024 | Formatos de fecha | Normalizar fechas a AAAA-MM | 1,080 | 1,080 |
| 2024 | Municipios con alias, tildes o errores | Normalizar a nombre oficial y DIVIPOLA | 32 | 15 |
| 2024 | Segmentos no estandarizados | Unificar categorías y marcar vacíos | 6 | 4 |
| 2024 | Segmentos vacíos | Marcar como 'No informado' | 3 | 0 |
| 2024 | Tipos de compra no estandarizados | Unificar a Bolsa o Contrato | 4 | 2 |
| 2024 | Energía expresada en MWh | Convertir MWh a kWh (× 1.000) | 337 | 337 |
| 2024 | Energía vacía, inválida o negativa | Enviar fila a cuarentena | 9 | 0 |
| 2024 | Valores COP vacíos | Conservar como nulo sin inventar el importe | 11 | 11 |
| 2024 | Llaves mensuales duplicadas | Conservar primera fila y enviar conflicto a cuarentena | 0 | 0 |
| 2024 | Filas enviadas a cuarentena | Conservar todas las filas no corregibles con motivo | 9 | 9 |
| 2024 | Filas limpias | Validar esquema de ventas | 1,080 | 1,071 |
| 2024 | Filas de bronce recibidas | Detectar encabezado, preámbulo y filas de datos | 1,114 | 1,114 |
| 2025 | Títulos y notas antes del encabezado | Localizar encabezado y excluir preámbulo | 3 | 0 |
| 2025 | Encabezado guardado como fila | Usarlo como nombres de columna | 1 | 0 |
| 2025 | Filas de totales | Excluir filas TOTAL | 1 | 0 |
| 2025 | Filas vacías | Excluir filas sin ningún dato | 0 | 0 |
| 2025 | Filas duplicadas exactas | Conservar una sola copia | 32 | 0 |
| 2025 | Formatos de fecha | Normalizar fechas a AAAA-MM | 1,080 | 1,080 |
| 2025 | Municipios con alias, tildes o errores | Normalizar a nombre oficial y DIVIPOLA | 30 | 15 |
| 2025 | Segmentos no estandarizados | Unificar categorías y marcar vacíos | 6 | 4 |
| 2025 | Segmentos vacíos | Marcar como 'No informado' | 6 | 0 |
| 2025 | Tipos de compra no estandarizados | Unificar a Bolsa o Contrato | 4 | 2 |
| 2025 | Energía expresada en MWh | Convertir MWh a kWh (× 1.000) | 0 | 0 |
| 2025 | Energía vacía, inválida o negativa | Enviar fila a cuarentena | 9 | 0 |
| 2025 | Valores COP vacíos | Conservar como nulo sin inventar el importe | 4 | 4 |
| 2025 | Llaves mensuales duplicadas | Conservar primera fila y enviar conflicto a cuarentena | 0 | 0 |
| 2025 | Filas enviadas a cuarentena | Conservar todas las filas no corregibles con motivo | 9 | 9 |
| 2025 | Filas limpias | Validar esquema de ventas | 1,080 | 1,071 |
| 2025 | Filas de bronce recibidas | Detectar encabezado, preámbulo y filas de datos | 1,117 | 1,117 |
| 2026 | Títulos y notas antes del encabezado | Localizar encabezado y excluir preámbulo | 3 | 0 |
| 2026 | Encabezado guardado como fila | Usarlo como nombres de columna | 1 | 0 |
| 2026 | Filas de totales | Excluir filas TOTAL | 1 | 0 |
| 2026 | Filas vacías | Excluir filas sin ningún dato | 0 | 0 |
| 2026 | Filas duplicadas exactas | Conservar una sola copia | 24 | 0 |
| 2026 | Formatos de fecha | Normalizar fechas a AAAA-MM | 810 | 810 |
| 2026 | Municipios con alias, tildes o errores | Normalizar a nombre oficial y DIVIPOLA | 29 | 15 |
| 2026 | Segmentos no estandarizados | Unificar categorías y marcar vacíos | 6 | 4 |
| 2026 | Segmentos vacíos | Marcar como 'No informado' | 5 | 0 |
| 2026 | Tipos de compra no estandarizados | Unificar a Bolsa o Contrato | 4 | 2 |
| 2026 | Energía expresada en MWh | Convertir MWh a kWh (× 1.000) | 0 | 0 |
| 2026 | Energía vacía, inválida o negativa | Enviar fila a cuarentena | 9 | 0 |
| 2026 | Valores COP vacíos | Conservar como nulo sin inventar el importe | 6 | 6 |
| 2026 | Llaves mensuales duplicadas | Conservar primera fila y enviar conflicto a cuarentena | 0 | 0 |
| 2026 | Filas enviadas a cuarentena | Conservar todas las filas no corregibles con motivo | 9 | 9 |
| 2026 | Filas limpias | Validar esquema de ventas | 810 | 801 |
| 2026 | Filas de bronce recibidas | Detectar encabezado, preámbulo y filas de datos | 839 | 839 |

## ideam_precipitacion_diaria

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 29,804 | 29,804 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 29,804 | 29,804 |

## ideam_temperatura_diaria

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 17,349 | 17,349 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 17,349 | 17,349 |

## nasa_power_clima_diario

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 1,004 | 1,004 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 61 | 61 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 1,004 | 1,004 |

## noaa_oni_mensual

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 920 | 920 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 920 | 920 |
| — | Trimestres asignados al mes central | — | 920 | 920 |

## xm_aportes_energia_diarios

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 1,004 | 1,004 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 1,004 | 1,004 |

## xm_demanda_horaria

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 1,004 | 24,096 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 1,004 | 24,096 |

## xm_embalses_diarios

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 1,004 | 1,004 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 1,004 | 1,004 |

## xm_generacion_recurso_horaria

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 350,361 | 8,408,664 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 2,473,215 | 2,473,215 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 350,361 | 8,408,664 |

## xm_listado_recursos

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 2,493 | 2,491 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 2 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 2,493 | 2,491 |

## xm_precio_bolsa_horario

| Año | Problema de calidad | Regla aplicada | Antes | Después |
|---:|---|---|---:|---:|
| — | Registros en la fuente | Clasificar las filas entre plata y cuarentena | 1,004 | 24,096 |
| — | Valores vacíos no imputables | Conservarlos como nulos; no inventar valores | 0 | 0 |
| — | Filas duplicadas o conflictos de llave | Conservar una fila o separar el conflicto | 0 | 0 |
| — | Filas inválidas enviadas a cuarentena | Preservar la fila con el motivo de rechazo | 0 | 0 |
| — | Filas válidas | Validar el esquema Pandera antes de guardar | 1,004 | 24,096 |
