select
    cast(fecha as date) as fecha,
    cast(oni as double) as oni,
    cast(fase_enso as varchar) as fase_enso
from {{ source('plata', 'noaa_oni_mensual') }}
