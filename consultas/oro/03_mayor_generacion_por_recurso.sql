select
    recurso.codigo_recurso,
    recurso.nombre_recurso,
    recurso.tipo,
    round(sum(generacion.generacion), 2) as generacion_reportada_acumulada
from fact_generacion_recurso as generacion
join dim_recurso as recurso using (codigo_recurso)
group by recurso.codigo_recurso, recurso.nombre_recurso, recurso.tipo
order by generacion_reportada_acumulada desc
limit 5
