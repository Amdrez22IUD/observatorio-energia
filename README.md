# Observatorio Energía y Clima – Equipo <nombre></nombre>

> Proyecto Integrado IV – Integración de Información · IU Digital de Antioquia · 2026-2

## 👥 Integrantes

| Nombre                 | Usuario GitHub | Rol                             |
| ---------------------- | -------------- | ------------------------------- |
| Andres Cuenta Personal | amdrez22       | Líder técnico / Data Engineer |
| Andres Mejia Pelaez    | amdrez22IUD    | Analytics Engineer              |
|                        |                | Data Quality Analyst            |
|                        |                | BI Analyst / Storyteller        |

## 🎯 Objetivo

Integrar datos del mercado eléctrico (XM), del clima (IDEAM y NOAA) y de ventas internas (EnerAndes) para analizar el riesgo energético de Colombia ante El Niño 2026.

## 📦 Fuentes de datos (capa bronce)

| Fuente                | Tipo                  | Archivo en `data/bronze/`                            |
| --------------------- | --------------------- | ------------------------------------------------------ |
| XM – API Sinergox    | API REST (POST, JSON) | `xm_precio_bolsa`, `xm_demanda`, `xm_embalses`, `xm_generacion_recurso`, `xm_aportes_energia`, `xm_listado_recursos` |
| IDEAM – datos.gov.co | API Socrata (SoQL)    | `ideam_precipitacion_diaria`, `ideam_temperatura_diaria` (`sbwg-7ju4`) |
| NOAA – índice ONI   | Archivo de texto      | `noaa_oni`                                           |
| EnerAndes             | Excel interno         | `enerandes_ventas_2023` … `enerandes_ventas_2026` |

## ⚙️ Cómo ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# copiar ventas_enerandes_2023_2026.xlsx en data/insumos/
python -m src.pipeline          # descarga las fuentes configuradas a data/bronze/
python -m src.consultar         # consultas SQL de BI con DuckDB
python -m pytest                # ejecuta las pruebas
```

IDEAM descarga precipitacion diaria desde 2025 en Antioquia y resume temperatura horaria del aire (sensor a 2 m) en valores diarios por estacion. Los promedios, minimos y maximos se calculan en Socrata para reducir el volumen descargado. El [dataset de temperatura sbwg-7ju4](https://datos.gov.co/d/sbwg-7ju4) contiene datos crudos de sensores y el IDEAM advierte que pueden presentar errores; se deben validar antes de usos sensibles.

Para volver a descargar todo: `python -m src.pipeline --forzar`. El rango de fechas se cambia en `src/config.py`. XM descarga sus metricas horarias y diarias en ventanas de hasta 30 dias, mientras que `ListadoRecursos` usa el endpoint `lists` sin fechas.

## 🏗️ Arquitectura

```
Fuentes -> BRONCE (dato tal cual + linaje) -> PLATA (limpio) -> ORO (modelo estrella) -> Dashboard
```

## 🤖 Uso de IA

(Declarar aquí qué herramientas de IA se usaron y para qué.)
