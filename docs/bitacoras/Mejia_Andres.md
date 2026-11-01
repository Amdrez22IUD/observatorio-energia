# Bitácora individual — Evidencia 2

## Identificación

| Campo | Detalle |
|---|---|
| Estudiante | Andrés Mejía Peláez |
| Usuario de GitHub | `amdrez22IUD` |
| Rol en el equipo | Analytics Engineer |
| Evidencia | EA2: Calidad de datos y modelo dimensional |

## Actividades y aportes

| Fecha | Actividad | Resultado |
|---|---|---|
| 2026-10-31 | Amplié la limpieza de EnerAndes a las hojas 2023–2026. Incorporé la normalización de fechas y unidades, reglas para municipios y categorías, métricas de calidad y cuarentena. | La transformación conserva 4.007 filas válidas y 43 filas en cuarentena de 4.184 filas recibidas. Pull request #16. |
| 2026-10-31 | Implementé las transformaciones y validaciones de las fuentes XM, IDEAM, NOAA ONI y NASA POWER; agregué pruebas para las reglas de limpieza. | Las tablas plata se validan con Pandera; XM horario queda en formato largo y ONI se asigna a su mes central con fase ENSO. Pull request #17. |
| 2026-10-31 | Amplié el modelo dbt/DuckDB con dimensiones y hechos para ventas, mercado horario y generación por recurso. | El modelo dimensional conserva las relaciones con el catálogo de recursos y sus pruebas dbt. Pull request #18. |
| 2026-10-31 | Implementé la orquestación de plata y oro, el reporte consolidado de calidad, las consultas de negocio y la documentación del modelo. | `python -m src.transformar` ejecuta las transformaciones y `dbt build`; se documentaron las consultas y el diccionario de datos. Pull request #19. |

## Evidencia de colaboración

| Commit | Aporte | Pull request |
|---|---|---|
| `551e27b` | Limpieza multianual de EnerAndes, reporte y pruebas. | [#16](https://github.com/Amdrez22IUD/observatorio-energia/pull/16) |
| `313aecc` | Limpieza y pruebas de las demás fuentes. | [#17](https://github.com/Amdrez22IUD/observatorio-energia/pull/17) |
| `e197b75` | Hechos, dimensiones y pruebas del esquema estrella. | [#18](https://github.com/Amdrez22IUD/observatorio-energia/pull/18) |
| `3aff959` | Orquestación, reporte, diccionario, consultas y documentación. | [#19](https://github.com/Amdrez22IUD/observatorio-energia/pull/19) |

## Validación

- `python -m pytest -q`: 39 pruebas aprobadas.
- `python -m src.transformar`: ejecución completa de plata y oro; `dbt build` finalizó con 48 pruebas aprobadas y sin errores.
- `python -m src.consultar`: ejecución correcta de las consultas SQL de bronce y oro.
- `git diff --check`: sin errores de formato.

## Reflexión

El trabajo conectó las reglas de calidad con el modelo analítico: conservar las filas no corregibles en cuarentena permitió medir los problemas sin perder evidencia, y las pruebas de Pandera y dbt ayudaron a validar tanto las tablas limpias como las relaciones del esquema estrella. La orquestación dejó un flujo reproducible para construir las capas plata y oro desde los datos bronce disponibles.

## Pendientes individuales de entrega

- Enlace al video individual de sustentación: pendiente de agregar.
