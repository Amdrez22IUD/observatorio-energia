select
    fecha.fase_enso,
    count(distinct mercado.fecha_id) as dias,
    round(avg(mercado.precio_bolsa), 2) as precio_promedio_cop_kwh,
    round(avg(mercado.demanda), 0) as demanda_promedio
from fact_mercado_horario as mercado
join dim_fecha as fecha using (fecha_id)
where fecha.anio between 2024 and 2026
group by fecha.fase_enso
order by fecha.fase_enso
