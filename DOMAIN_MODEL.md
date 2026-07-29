# Modelo de Dominio — AppleHealthAnalytics

## 1. Objetivo del dominio

Representar los datos de salud del usuario de forma **independiente del XML de Apple Health**, de modo que el resto del sistema (repositorio, exportación, resúmenes) opere sobre **entidades propias del dominio** y no sobre diccionarios ni estructuras ligadas al formato de origen.

El dominio actual cubre las métricas definidas en el SPEC v0.1:

- Heart Rate
- Heart Rate Variability (SDNN)
- Step Count
- Active Energy Burned
- Workout

---

## 2. Entidades existentes

### HealthRecord

**Archivo:** `applehealth/models.py`

Representa una **observación o medición individual** de salud: un tipo, un valor, una unidad y un intervalo temporal.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `identificador` | `str \| None` | Identificador único del registro |
| `tipo_registro` | `str \| None` | Tipo HK (p. ej. `HKQuantityTypeIdentifierHeartRate`) |
| `fecha_inicio` | `datetime \| None` | Inicio del intervalo de la medición |
| `fecha_fin` | `datetime \| None` | Fin del intervalo de la medición |
| `fecha_creacion` | `datetime \| None` | Creación en la fuente de origen |
| `fecha_modificacion` | `datetime \| None` | Última modificación en la fuente |
| `fuente_origen` | `str \| None` | Aplicación o servicio origen |
| `dispositivo` | `str \| None` | Dispositivo que capturó la medición |
| `unidad_medida` | `str \| None` | Unidad del valor |
| `valor` | `float \| None` | Magnitud numérica |
| `metadatos` | `dict[str, Any]` | Información adicional (p. ej. `source_version`) |

**Origen XML:** elemento `<Record>` filtrado por tipo HK.

**Tipos procesados actualmente:**

| Tipo HK | Tabla SQLite |
|---------|--------------|
| `HKQuantityTypeIdentifierHeartRate` | `heart_rate` |
| `HKQuantityTypeIdentifierHeartRateVariabilitySDNN` | `hrv` |
| `HKQuantityTypeIdentifierStepCount` | `step_count` |
| `HKQuantityTypeIdentifierActiveEnergyBurned` | `active_energy` |

---

### WorkoutRecord

**Archivo:** `applehealth/workout.py`

Representa una **sesión de actividad física**: un evento con múltiples métricas agregadas (duración, distancia, energía), no una medición puntual.

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `identificador` | `str \| None` | Identificador único del entrenamiento |
| `tipo_actividad` | `str \| None` | Tipo de actividad (p. ej. `HKWorkoutActivityTypeRunning`) |
| `fecha_inicio` | `datetime \| None` | Inicio del entrenamiento |
| `fecha_fin` | `datetime \| None` | Fin del entrenamiento |
| `fecha_creacion` | `datetime \| None` | Creación en la fuente de origen |
| `fecha_modificacion` | `datetime \| None` | Última modificación en la fuente |
| `duracion` | `float \| None` | Duración total |
| `unidad_duracion` | `str \| None` | Unidad de la duración |
| `distancia_total` | `float \| None` | Distancia recorrida |
| `unidad_distancia` | `str \| None` | Unidad de la distancia |
| `energia_total` | `float \| None` | Energía consumida |
| `unidad_energia` | `str \| None` | Unidad de la energía |
| `fuente_origen` | `str \| None` | Aplicación o servicio origen |
| `dispositivo` | `str \| None` | Dispositivo que registró la sesión |
| `metadatos` | `dict[str, Any]` | Atributos XML no mapeados explícitamente |

**Origen XML:** elemento `<Workout>`.

**Tabla SQLite:** `workouts`

---

## 3. Relación entre entidades

`WorkoutRecord` **no es una especialización** de `HealthRecord`. Son entidades independientes:

- Un **WorkoutRecord** es un evento contenedor (sesión de actividad).
- Durante un entrenamiento pueden generarse múltiples **HealthRecord** (frecuencia cardíaca, energía, etc.).
- La asociación entre ambos se establece por **coincidencia temporal** (registros cuyo intervalo cae dentro del entrenamiento) o por identificadores de la fuente, cuando estén disponibles.
- Los **HealthRecord** conservan identidad propia y pueden existir sin estar vinculados a ningún entrenamiento.

```
WorkoutRecord (1) ──→ (N) HealthRecord
         asociación por intervalo temporal
```

---

## 4. Flujo de datos

```
export.xml
    │
    ▼
StreamParser (applehealth/parser/stream_parser.py)
    │
    ├── <Record>  →  _quantity_record()  →  HealthRecord
    │
    └── <Workout> →  _workout_record()    →  WorkoutRecord
    │
    ▼
RecordRepository (applehealth/db/repository.py)
    │
    ├── add_quantity(table, HealthRecord)   →  heart_rate | hrv | step_count | active_energy
    │
    └── add_workout(WorkoutRecord)          →  workouts
    │
    ▼
SQLite (health.sqlite)
    │
    ▼
CSV + summary.json / summary.md
```

El repositorio actúa como **capa de adaptación** entre las entidades de dominio (atributos en español, `datetime`) y el esquema SQLite existente (columnas en inglés, fechas como texto).

---

## 5. Entidades deliberadamente NO creadas

| Entidad considerada | Motivo |
|---------------------|--------|
| **BodyCompositionRecord** | Peso, grasa corporal, IMC y masa magra son mediciones puntuales (`<Record>` con valor y unidad). `HealthRecord` las representa correctamente con `tipo_registro`. |
| **HeartRateRecord**, **HRVRecord**, etc. | Especializaciones por tipo HK innecesarias; todas son `HealthRecord` diferenciadas por `tipo_registro`. |
| **ActivitySummary** | Resúmenes diarios agregados (anillos Move/Exercise/Stand), no mediciones puntuales. Fuera del alcance v0.1. |
| **Correlation** | Agrupa varias mediciones relacionadas en una observación lógica. Estructura XML distinta, no procesada. |
| **Me / perfil de usuario** | Características estáticas (fecha de nacimiento, sexo). No son series temporales ni mediciones. |
| **ClinicalRecord** | Documentos clínicos (artefactos FHIR), no magnitudes numéricas con unidad. |
| **ExportDate** | Metadato de exportación leído por el parser; no es entidad de dominio persistida. |
