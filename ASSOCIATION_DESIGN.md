# Diseño técnico — Módulo de asociación WorkoutRecord ↔ HealthRecord

Documento derivado de `NEXT_MODULE.md`. Versión objetivo: v0.1.

---

## 1. Objetivo

Establecer la relación entre `WorkoutRecord` y `HealthRecord` para determinar qué mediciones ocurrieron durante cada entrenamiento y proporcionar ese resultado a las capas superiores del sistema.

El módulo opera exclusivamente sobre entidades de dominio y encapsula toda la lógica de asociación temporal, de modo que el resto del sistema no necesite implementar ni conocer dichas reglas.

### Alcance v0.1

- Criterio de asociación exclusivamente temporal (contención total, límites inclusivos).
- Sin introducir nuevas entidades de dominio.
- Sin responsabilidades de persistencia, consulta ni presentación.
- Procesamiento completo en memoria.
- Ejecución determinista con recálculo completo en cada ejecución.

---

## 2. Componentes

| Componente | Descripción |
|------------|-------------|
| **AssociationService** | Orquestador principal. Recibe colecciones de entidades, ejecuta el proceso de asociación y devuelve el resultado agregado. |
| **TemporalMatcher** | Evalúa si un `HealthRecord` está contenido temporalmente dentro de un `WorkoutRecord` según las reglas v0.1. |
| **AssociationSelector** | Resuelve conflictos cuando un `HealthRecord` coincide con más de un `WorkoutRecord`, eligiendo la coincidencia más específica. |
| **EligibilityFilter** | Descarta entidades sin `fecha_inicio` y `fecha_fin` definidos antes de evaluar asociaciones. |

---

## 3. Flujo de ejecución

```
1. Entrada
   ├── Iterable[WorkoutRecord]
   └── Iterable[HealthRecord]   (tipos SPEC v0.1)

2. Filtrado de elegibilidad (EligibilityFilter)
   ├── WorkoutRecord  → conservar solo si fecha_inicio AND fecha_fin presentes
   └── HealthRecord   → conservar solo si fecha_inicio AND fecha_fin presentes

3. Para cada HealthRecord elegible:
   ├── Evaluar contención temporal contra cada WorkoutRecord elegible (TemporalMatcher)
   ├── Recopilar WorkoutRecord candidatos que contengan el intervalo completo
   └── Si hay más de un candidato → AssociationSelector elige el más específico

4. Construcción del resultado (AssociationResult)
   ├── Agrupar HealthRecord por WorkoutRecord asociado
   ├── Identificar WorkoutRecord sin mediciones asociadas
   └── Identificar HealthRecord sin entrenamiento asociado

5. Salida
   └── AssociationResult (determinista, recalculado por completo)
```

Regla temporal v0.1 (contención inclusiva):

```
WorkoutRecord.fecha_inicio  ≤  HealthRecord.fecha_inicio
HealthRecord.fecha_fin      ≤  WorkoutRecord.fecha_fin
```

---

## 4. Responsabilidades de cada componente

### AssociationService

- Recibir exclusivamente entidades de dominio (`WorkoutRecord`, `HealthRecord`).
- Coordinar filtrado, matching, selección y construcción del resultado.
- Garantizar determinismo: misma entrada → misma salida.
- No acceder a SQLite, parser ni repositorio.

### EligibilityFilter

- Excluir entidades con `fecha_inicio` o `fecha_fin` ausentes.
- No inferir ni completar fechas faltantes.

### TemporalMatcher

- Determinar si el intervalo completo de un `HealthRecord` está contenido dentro del intervalo de un `WorkoutRecord`.
- Aplicar límites inclusivos en ambos extremos.
- No usar solapamiento parcial, heurísticas ni `metadatos`.

### AssociationSelector

- Garantizar como máximo una asociación por `HealthRecord`.
- Ante múltiples `WorkoutRecord` candidatos, seleccionar la coincidencia más específica según criterio temporal.
- No generar asociaciones múltiples.

---

## Objetos de salida

### AssociationResult

DTO (Data Transfer Object) o contrato de salida del módulo. No es un componente con lógica ni una entidad de dominio.

- Contenedor del resultado: agrupaciones, registros huérfanos y entrenamientos vacíos.
- Exponer agrupaciones WorkoutRecord → HealthRecord[].
- Exponer listas de entrenamientos sin mediciones y mediciones sin entrenamiento.
- Servir como contrato de salida sin imponer formato de persistencia.

---

## 5. Interfaces públicas propuestas

Solo firmas y propósito. Sin implementación.

```python
# applehealth/association/service.py

def associate(
    workouts: Sequence[WorkoutRecord],
    records: Sequence[HealthRecord],
) -> AssociationResult:
    """Ejecuta el proceso completo de asociación v0.1 y devuelve el resultado."""
```

```python
# applehealth/association/matcher.py

def is_contained(
    record: HealthRecord,
    workout: WorkoutRecord,
) -> bool:
    """True si el intervalo completo del HealthRecord está contenido en el WorkoutRecord (inclusivo)."""
```

```python
# applehealth/association/selector.py

def select_best_workout(
    record: HealthRecord,
    candidates: Sequence[WorkoutRecord],
) -> WorkoutRecord | None:
    """Elige el WorkoutRecord más específico entre candidatos válidos; None si la secuencia está vacía."""
```

```python
# applehealth/association/filter.py

def filter_eligible_workouts(
    workouts: Sequence[WorkoutRecord],
) -> list[WorkoutRecord]:
    """Devuelve workouts con fecha_inicio y fecha_fin definidos."""

def filter_eligible_records(
    records: Sequence[HealthRecord],
) -> list[HealthRecord]:
    """Devuelve HealthRecord con fecha_inicio y fecha_fin definidos."""
```

### AssociationResult

Contrato de salida del módulo de asociación.

La estructura concreta del resultado permanece intencionalmente sin definir en v0.1 y será especificada una vez que se establezca el criterio definitivo de identidad, agrupación y representación de las asociaciones.

---

## 6. Integración con el parser, modelos y repositorio existentes

### Modelos (`HealthRecord`, `WorkoutRecord`)

- El módulo **consume** las entidades existentes sin modificarlas.
- Tipos elegibles v0.1: frecuencia cardíaca, HRV (SDNN), energía activa y conteo de pasos (todos los `HealthRecord` que el SPEC actual soporta).
- No se excluyen tipos por ser potencialmente agregados; la elegibilidad depende solo de la regla temporal y de fechas completas.

### Parser (`stream_parser.py`)

- El parser **no invoca** el módulo de asociación.
- Produce `HealthRecord` y `WorkoutRecord` de forma independiente.
- Una capa superior (pipeline, script o consulta) cargará las entidades ya construidas y las pasará a `associate()`.

### Repositorio (`RecordRepository`)

- El repositorio **no participa** en la lógica de asociación v0.1.
- Persiste entidades en tablas separadas (`heart_rate`, `hrv`, `step_count`, `active_energy`, `workouts`).
- Si una capa externa necesita asociaciones desde SQLite, deberá:
  1. Reconstruir `HealthRecord` / `WorkoutRecord` desde la base de datos.
  2. Invocar `associate()`.
  3. Decidir cómo almacenar, consultar o presentar el `AssociationResult` (tabla de relación, resumen, CSV derivado, etc.).

### Punto de integración propuesto

```
Parser → entidades de dominio → [capa invocadora] → associate() → AssociationResult → [persistencia / exportación / resumen]
```

El módulo ocupa el espacio entre entidades de dominio ya materializadas y cualquier consumidor downstream.

---

## 7. Estrategia de pruebas

### Pruebas unitarias

| Área | Casos |
|------|-------|
| **TemporalMatcher** | Contención total válida; límites inclusivos (inicio/fin exactos); rechazo por solapamiento parcial; rechazo por intervalo exterior |
| **EligibilityFilter** | Exclusión cuando falta `fecha_inicio`, `fecha_fin` o ambos; conservación cuando ambos presentes |
| **AssociationSelector** | Un candidato → selección directa; múltiples candidatos → más específico; ningún candidato → None |
| **AssociationService** | Flujo completo determinista; recálculo idéntico en ejecuciones repetidas |

### Pruebas de integración

- Conjuntos sintéticos de `WorkoutRecord` + `HealthRecord` que simulen escenarios del SPEC v0.1.
- Verificar agrupaciones, entrenamientos vacíos y mediciones huérfanas.
- Confirmar que un `HealthRecord` nunca aparece en más de un grupo.

### Datos de prueba sugeridos

- Entrenamiento con mediciones de frecuencia cardíaca contenidas.
- Entrenamiento sin mediciones asociadas.
- Medición fuera de cualquier entrenamiento.
- Medición contenida en dos entrenamientos anidados (desempate por especificidad).
- Registros con fechas ausentes (deben ignorarse).
- Registro agregado por día (step count) que cumple contención temporal (no excluido en v0.1).

### Criterios de aceptación

- Misma entrada → misma salida (determinismo).
- Sin acceso a SQLite, parser ni repositorio en tests del módulo.
- Sin nueva entidad de dominio en el resultado.

---

## 8. Riesgos técnicos

| Riesgo | Descripción | Mitigación propuesta en diseño |
|--------|-------------|--------------------------------|
| **Memoria** | v0.1 carga todo en memoria; exportaciones grandes pueden agotar RAM. | Documentar límite; diferir procesamiento incremental a versiones futuras. |
| **Registros agregados** | Step count diario puede cumplir contención temporal dentro de un entrenamiento y producir asociaciones semánticamente cuestionables. | Aceptado en v0.1; reglas específicas reservadas para versiones futuras. |
| **Desempate ambiguo** | "Coincidencia más específica" no está formalizada numéricamente en `NEXT_MODULE.md`. | Definir criterio explícito en implementación (p. ej. menor duración de intervalo del workout). |
| **Identidad en resultados** | `AssociationResult.by_workout` usa `WorkoutRecord` como clave; instancias duplicadas o sin identificador dificultan comparación. | Consumidor debe proveer entidades con identidad estable o aceptar agrupación por referencia/objeto. |
| **Reconstrucción desde SQLite** | Capa invocadora debe mapear filas SQL → entidades antes de asociar; duplica lógica del repositorio inverso. | Responsabilidad explícita de capa externa; no forma parte del módulo v0.1. |
| **Recálculo completo** | Cada ejecución reprocessa todo; coste crece linealmente con volumen. | Aceptado en v0.1; sin cache ni actualización incremental. |
| **Sin metadatos** | Identificadores Apple Health ignorados; asociaciones puramente temporales pueden ser imprecisas en casos límite. | Aceptado en v0.1; criterio prioritario por metadatos reservado para versiones futuras. |
