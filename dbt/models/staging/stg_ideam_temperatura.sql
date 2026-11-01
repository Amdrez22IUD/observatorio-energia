select
    cast(fecha as date) as fecha,
    cast(codigo_estacion as varchar) as codigo_estacion,
    cast(nombre_estacion as varchar) as nombre_estacion,
    cast(municipio as varchar) as municipio,
    cast(latitud as double) as latitud,
    cast(longitud as double) as longitud,
    cast(temperatura_promedio_c as double) as temperatura_promedio_c,
    cast(temperatura_minima_c as double) as temperatura_minima_c,
    cast(temperatura_maxima_c as double) as temperatura_maxima_c,
    cast(n_observaciones as integer) as n_observaciones
from {{ source('plata', 'ideam_temperatura_diaria') }}
