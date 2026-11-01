select
    fecha_dim.fecha_id,
    hora_dim.hora_id,
    generacion.codigo_recurso,
    generacion.generacion
from {{ ref('stg_xm_generacion_recurso') }} as generacion
join {{ ref('dim_fecha') }} as fecha_dim
    on generacion.fecha = fecha_dim.fecha
join {{ ref('dim_hora') }} as hora_dim
    on generacion.hora = hora_dim.hora
join {{ ref('dim_recurso') }} as recurso
    on generacion.codigo_recurso = recurso.codigo_recurso
