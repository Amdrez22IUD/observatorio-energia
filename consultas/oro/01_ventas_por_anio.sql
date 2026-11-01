select
    mes.anio,
    round(sum(ventas.energia_kwh), 0) as energia_total_kwh,
    round(sum(ventas.valor_cop), 0) as valor_total_cop,
    sum(ventas.clientes) as clientes_reportados
from fact_ventas_mensual as ventas
join dim_mes as mes using (mes_id)
group by mes.anio
order by mes.anio
