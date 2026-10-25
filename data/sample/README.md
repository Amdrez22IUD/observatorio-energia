# Muestras publicas

Estos CSV son muestras pequenas para explorar el esquema y probar el pipeline; no reemplazan los datos completos de `data/bronze/`. Al ejecutar `python -m src.documentar_datos`, se actualizan con las primeras 200 filas disponibles de cada Parquet.

| Archivo | Fuente | Contenido |
| --- | --- | --- |
| `xm_precio_bolsa.csv` | XM | Precio horario de bolsa |
| `xm_demanda.csv` | XM | Demanda horaria del sistema |
| `xm_embalses.csv` | XM | Nivel diario agregado de embalses |
| `xm_generacion_recurso.csv` | XM | Generacion horaria por recurso |
| `xm_aportes_energia.csv` | XM | Aportes diarios de energia |
| `xm_listado_recursos.csv` | XM | Catalogo de recursos vigente al momento de la consulta |
| `ideam_precipitacion_diaria.csv` | IDEAM, dataset `s54a-sgyg` | Precipitacion diaria por estacion |
| `ideam_temperatura_diaria.csv` | IDEAM, dataset `sbwg-7ju4` | Resumen diario de temperatura por estacion |
| `nasa_power_clima_diario.csv` | NASA POWER | Temperatura, precipitacion y radiacion solar para el punto configurado |
| `noaa_oni.csv` | NOAA | Registros del ONI |
| `enerandes_ventas_2023.csv` … `enerandes_ventas_2026.csv` | EnerAndes | Primeras filas de las hojas de ventas anuales |

Las muestras temporales incluidas en el repositorio pueden corresponder a una extraccion puntual; los rangos y la fecha de extraccion se consultan en sus columnas de linaje cuando estan presentes. Cada archivo contiene como maximo 200 filas. El equipo confirma que el archivo de EnerAndes usado en esta actividad es recreativo y educativo.

El perfil reproducible y la exportacion de muestras se ejecutan desde la raiz del proyecto:

```powershell
python -m src.documentar_datos
python -m src.perfilamiento
```
