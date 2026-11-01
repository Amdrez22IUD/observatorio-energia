select
    hora as hora_id,
    hora,
    lpad(cast(hora as varchar), 2, '0') || ':00' as hora_inicio,
    case
        when hora between 0 and 5 then 'Madrugada'
        when hora between 6 and 11 then 'Mañana'
        when hora between 12 and 17 then 'Tarde'
        else 'Noche'
    end as franja_horaria
from range(1, 25) as horas(hora)
