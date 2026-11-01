select
    cast(fecha as date) as fecha,
    cast(hora as integer) as hora,
    cast(codigo as varchar) as codigo,
    cast(precio_bolsa as double) as precio_bolsa
from {{ source('plata', 'xm_precio_bolsa_horario') }}
