select
    cast(fecha as date) as fecha,
    cast(hora as integer) as hora,
    cast(codigo_recurso as varchar) as codigo_recurso,
    cast(generacion as double) as generacion
from {{ source('plata', 'xm_generacion_recurso_horaria') }}
