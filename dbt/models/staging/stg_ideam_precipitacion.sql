select
    cast(fecha as date) as fecha,
    cast(codigo_estacion as varchar) as codigo_estacion,
    cast(nombre_estacion as varchar) as nombre_estacion,
    cast(municipio as varchar) as municipio,
    cast(latitud as double) as latitud,
    cast(longitud as double) as longitud,
    cast(precipitacion_mm as double) as precipitacion_mm,
    cast(n_observaciones as integer) as n_observaciones
from {{ source('plata', 'ideam_precipitacion_diaria') }}
