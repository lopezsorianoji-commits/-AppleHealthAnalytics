# Modelo de Datos

## Propósito

Este documento define el modelo de datos del conector Apple Health.

Su objetivo es establecer una representación independiente del XML de Apple Health, de manera que el resto del sistema trabaje con entidades propias del dominio y no con la estructura interna del archivo de origen.

---

## Principios

1. El modelo representa conceptos del dominio, no elementos XML.

2. El modelo debe permanecer estable aunque cambie el formato de importación.

3. Todas las consultas del sistema deberán realizarse sobre este modelo.

4. El modelo deberá poder reutilizarse con otras fuentes de datos de salud en el futuro.

---

## Entidades

### HealthRecord

Representa una observación o medición individual relacionada con el estado de salud del usuario.

Constituye la entidad base del dominio de salud y es independiente del origen de los datos.

Todos los registros especializados deberán derivarse conceptualmente de esta entidad.

#### Atributos comunes

- Identificador
- Tipo de registro
- Fecha de inicio
- Fecha de fin
- Fecha de creación
- Fecha de modificación
- Fuente de origen
- Dispositivo
- Unidad de medida
- Valor
- Metadatos

### Workout

Representa una sesión de actividad física realizada por el usuario.

Un entrenamiento constituye un evento dentro del historial de salud y puede estar asociado con múltiples registros de salud generados durante su ejecución.

No se considera una especialización de HealthRecord, sino una entidad independiente con relaciones hacia los registros que ocurrieron durante el entrenamiento.

---

## Relaciones

### Workout → HealthRecord

Un entrenamiento puede estar asociado con múltiples registros de salud ocurridos durante su intervalo temporal.

La asociación entre un entrenamiento y un HealthRecord se establece mediante la coincidencia de fechas y horas, o mediante identificadores proporcionados por la fuente de datos cuando estén disponibles.

Los registros de salud conservan su identidad propia y pueden existir independientemente de cualquier entrenamiento.

---

## Reglas

### Importación incremental

El sistema debe considerar cada importación como una sincronización del repositorio de datos de salud.

Los registros previamente almacenados no deberán duplicarse.

Si un registro ya existe, deberá conservarse.

Si aparecen nuevos registros, deberán incorporarse.

La importación deberá ser idempotente: importar el mismo archivo varias veces deberá producir exactamente el mismo estado final.