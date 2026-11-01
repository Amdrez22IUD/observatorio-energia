select
    cast(codigo_recurso as varchar) as codigo_recurso,
    cast(nombre_recurso as varchar) as nombre_recurso,
    cast(tipo as varchar) as tipo,
    cast(disponibilidad as varchar) as disponibilidad,
    cast(tipo_recurso as varchar) as tipo_recurso,
    cast(codigo_empresa as varchar) as codigo_empresa,
    cast(fuente_energia as varchar) as fuente_energia,
    cast(fecha_inicio_operacion as date) as fecha_inicio_operacion,
    cast(estado as varchar) as estado
from {{ source('plata', 'xm_listado_recursos') }}
