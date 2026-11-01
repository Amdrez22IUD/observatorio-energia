with fechas_fuente as (
    select cast(periodo || '-01' as date) as fecha
    from {{ ref('stg_ventas') }}

    union all

    select fecha from {{ ref('stg_xm_precio_bolsa') }}

    union all

    select fecha from {{ ref('stg_xm_demanda') }}

    union all

    select fecha from {{ ref('stg_xm_generacion_recurso') }}

    union all

    select fecha from {{ ref('stg_ideam_precipitacion') }}

    union all

    select fecha from {{ ref('stg_ideam_temperatura') }}

    union all

    select fecha from {{ ref('stg_noaa_oni') }}
),
limites as (
    select min(fecha) as fecha_minima, max(fecha) as fecha_maxima
    from fechas_fuente
),
calendario as (
    select cast(generada.fecha as date) as fecha
    from limites
    cross join generate_series(
        limites.fecha_minima,
        limites.fecha_maxima,
        interval 1 day
    ) as generada(fecha)
)
select
    cast(strftime(calendario.fecha, '%Y%m%d') as integer) as fecha_id,
    calendario.fecha,
    extract(year from calendario.fecha)::integer as anio,
    extract(month from calendario.fecha)::integer as mes,
    extract(quarter from calendario.fecha)::integer as trimestre,
    extract(day from calendario.fecha)::integer as dia,
    extract(isodow from calendario.fecha)::integer as dia_semana_num,
    strftime(calendario.fecha, '%A') as dia_semana,
    coalesce(noaa.fase_enso, 'Neutral') as fase_enso
from calendario
left join {{ ref('stg_noaa_oni') }} as noaa
    on date_trunc('month', calendario.fecha) = noaa.fecha
