# AppleHealthAnalytics v0.1

## Objetivo

Desarrollar una aplicación local para macOS que procese exportaciones XML de Apple Health de cualquier tamaño utilizando procesamiento en streaming.

Todo el procesamiento será local.

---

## Datos a extraer

- Heart Rate

- Heart Rate Variability (SDNN)

- Workout

- Step Count

- Active Energy Burned

---

## Salidas

- health.sqlite

- HeartRate.csv

- HRV.csv

- Workouts.csv

- Steps.csv

- ActiveEnergy.csv

- summary.json

- [summary.md](http://summary.md)

---

## Restricciones

- No cargar el XML completo en memoria.

- Utilizar SQLite.

- Utilizar Python 3.12.

- Código modular.

- Compatible con archivos superiores a 5 GB.

---

## Primera versión

La versión 0.1 debe:

1. Leer exportar.xml.

2. Crear la base SQLite.

3. Exportar CSV.

4. Generar un resumen.