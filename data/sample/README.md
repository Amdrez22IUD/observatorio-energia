# Muestras publicas

Estos CSV son muestras pequenas para explorar el esquema y probar el pipeline; no reemplazan los datos completos de `data/bronze/`.

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

Las muestras temporales corresponden al 1-7 de enero de 2025, salvo el catalogo de recursos y el ONI, que son instantaneas o series estacionales. Cada archivo contiene como maximo diez filas. Se excluyeron los datos internos de EnerAndes; el Excel de ventas no debe publicarse.

El perfil reproducible se ejecuta desde la raiz del proyecto:

```powershell
python -m src.perfilamiento
```
