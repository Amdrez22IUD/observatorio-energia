select
    cast(fecha as date) as fecha,
    cast(hora as integer) as hora,
    cast(codigo as varchar) as codigo,
    cast(demanda as double) as demanda
from {{ source('plata', 'xm_demanda_horaria') }}
