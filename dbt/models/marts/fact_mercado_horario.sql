with mercado as (
    select
        coalesce(precio.fecha, demanda.fecha) as fecha,
        coalesce(precio.hora, demanda.hora) as hora,
        coalesce(precio.codigo, demanda.codigo) as codigo_mercado,
        precio.precio_bolsa,
        demanda.demanda
    from {{ ref('stg_xm_precio_bolsa') }} as precio
    full outer join {{ ref('stg_xm_demanda') }} as demanda
        on precio.fecha = demanda.fecha
        and precio.hora = demanda.hora
        and precio.codigo = demanda.codigo
)
select
    fecha_dim.fecha_id,
    hora_dim.hora_id,
    mercado.codigo_mercado,
    mercado.precio_bolsa,
    mercado.demanda
from mercado
join {{ ref('dim_fecha') }} as fecha_dim
    on mercado.fecha = fecha_dim.fecha
join {{ ref('dim_hora') }} as hora_dim
    on mercado.hora = hora_dim.hora
