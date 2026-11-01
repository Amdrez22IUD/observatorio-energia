with catalogo as (
    select distinct
        codigo_recurso,
        nombre_recurso,
        tipo,
        disponibilidad,
        tipo_recurso,
        codigo_empresa,
        fuente_energia,
        fecha_inicio_operacion,
        estado
    from {{ ref('stg_xm_listado_recursos') }}
),
recursos_historicos as (
    select distinct generacion.codigo_recurso
    from {{ ref('stg_xm_generacion_recurso') }} as generacion
    left join catalogo
        on generacion.codigo_recurso = catalogo.codigo_recurso
    where catalogo.codigo_recurso is null
),
recursos_sin_catalogo as (
    select
        codigo_recurso,
        codigo_recurso as nombre_recurso,
        'Sin información' as tipo,
        'Sin información' as disponibilidad,
        'Sin información' as tipo_recurso,
        'Sin información' as codigo_empresa,
        'Sin información' as fuente_energia,
        cast(null as date) as fecha_inicio_operacion,
        'Sin información' as estado,
        false as en_catalogo
    from recursos_historicos
)
select
    codigo_recurso,
    nombre_recurso,
    tipo,
    disponibilidad,
    tipo_recurso,
    codigo_empresa,
    fuente_energia,
    fecha_inicio_operacion,
    estado,
    true as en_catalogo
from catalogo

union all

select
    codigo_recurso,
    nombre_recurso,
    tipo,
    disponibilidad,
    tipo_recurso,
    codigo_empresa,
    fuente_energia,
    fecha_inicio_operacion,
    estado,
    en_catalogo
from recursos_sin_catalogo
