# Siguiente módulo: Asociación WorkoutRecord ↔ HealthRecord

## 1. ¿Qué problema resolverá?

Hoy `WorkoutRecord` y `HealthRecord` existen como entidades independientes almacenadas por separado, sin vínculo explícito entre ellas. No es posible saber qué mediciones ocurrieron **durante** un entrenamiento concreto (frecuencia cardíaca, energía activa, etc.).

Este módulo resolverá esa carencia: establecerá y consultará la relación **WorkoutRecord (1) → (N) HealthRecord** por coincidencia temporal (y por identificadores de fuente cuando existan), permitiendo analizar el contexto fisiológico de cada sesión de actividad.

---

## 2. ¿Qué entradas recibirá?

- **`WorkoutRecord`**: entrenamientos con `fecha_inicio`, `fecha_fin` y metadatos (p. ej. `identificador`, `tipo_actividad`).
- **`HealthRecord`**: mediciones con `fecha_inicio`, `fecha_fin`, `tipo_registro` y `valor`.
- **Criterio de asociación**: intervalo temporal (el registro cae dentro del entrenamiento) y, si aplica, identificadores proporcionados por Apple Health en `metadatos`.
- Las entradas del módulo serán exclusivamente entidades de dominio (WorkoutRecord y HealthRecord). El origen de esas entidades (SQLite, parser, pruebas, etc.) será responsabilidad de la capa que invoque el módulo, no del propio módulo.

---

## 3. ¿Qué salidas producirá?

- **Asociaciones explícitas** entre un entrenamiento y las mediciones vinculadas (p. ej. lista de `HealthRecord` por `WorkoutRecord`, o pares `(workout_id, health_record_id)`).
- **Consultas respondibles**, como:
  - mediciones de frecuencia cardíaca durante un entrenamiento;
  - energía activa registrada en el intervalo de una sesión;
  - entrenamientos sin mediciones asociadas;
  - mediciones de salud no vinculadas a ningún entrenamiento.
- **Salida persistida o exportable** (tabla de relación en SQLite, campos en resumen, o artefacto derivado) que el resto del sistema pueda usar sin reimplementar la lógica de solapamiento temporal.

---

## Responsabilidades

- Determinar si un `HealthRecord` ocurrió durante el intervalo temporal de un `WorkoutRecord`.
- Establecer asociaciones entre entrenamientos y mediciones según criterios de dominio (solapamiento temporal e identificadores de fuente cuando existan).
- Agrupar las mediciones vinculadas a cada entrenamiento.
- Identificar entrenamientos sin mediciones asociadas.
- Identificar mediciones de salud no vinculadas a ningún entrenamiento.
- Construir asociaciones entre WorkoutRecord y HealthRecord sin decidir cómo se almacenan, consultan o presentan.
- Mantener la independencia respecto al origen de las entidades de entrada y respecto a su persistencia posterior.

---

## Decisiones pendientes

---

## Decisiones resueltas

- No se introducirá una nueva entidad de dominio. El módulo producirá asociaciones entre `WorkoutRecord` y `HealthRecord`; la representación técnica de esas asociaciones se decidirá durante el diseño.
- En la versión v0.1 serán elegibles todos los `HealthRecord` soportados por el SPEC actual: frecuencia cardíaca, variabilidad de la frecuencia cardíaca (SDNN), energía activa y conteo de pasos. La incorporación de nuevos tipos dependerá de futuras versiones del parser y del SPEC.
- En la versión v0.1 no se excluirá ningún tipo de `HealthRecord` por ser potencialmente agregado. La elegibilidad para asociarse dependerá únicamente de la regla temporal definida por el módulo. Si futuras versiones identifican registros agregados incompatibles con este criterio, se incorporarán reglas específicas.
- En la versión v0.1 un `HealthRecord` se considerará ocurrido durante un `WorkoutRecord` únicamente cuando el intervalo completo de la medición esté contenido dentro del intervalo del entrenamiento. No se utilizarán reglas de solapamiento parcial ni heurísticas.
- En la versión v0.1 los límites de los intervalos temporales serán inclusivos. Un `HealthRecord` podrá comenzar exactamente en `fecha_inicio` del `WorkoutRecord` y terminar exactamente en `fecha_fin` del `WorkoutRecord` sin perder la asociación.
- En la versión v0.1 únicamente participarán en el proceso de asociación entidades que tengan definidos `fecha_inicio` y `fecha_fin`. Si alguno de esos campos falta en un `WorkoutRecord` o en un `HealthRecord`, no se generará asociación y el módulo no intentará inferir valores faltantes.
- En la versión v0.1 las asociaciones se determinarán exclusivamente mediante el criterio temporal. Los `metadatos` se conservarán, pero no se utilizarán para asociar `HealthRecord` y `WorkoutRecord`. Si en versiones futuras se normalizan identificadores confiables, podrán incorporarse como criterio prioritario.
- En la versión v0.1 un `HealthRecord` podrá asociarse como máximo a un único `WorkoutRecord`. Si un registro coincide con más de un entrenamiento, se seleccionará la coincidencia más específica según el criterio temporal definido para el módulo. No se generarán asociaciones múltiples.
- En la versión v0.1 las asociaciones serán deterministas y se recalcularán completamente cada vez que se ejecute el proceso de asociación. No se conservarán resultados de ejecuciones anteriores ni se implementará actualización incremental.
- En la versión v0.1 el módulo operará sobre el conjunto completo de datos en memoria. No se optimizará para procesamiento incremental ni para volúmenes que excedan la memoria disponible.
