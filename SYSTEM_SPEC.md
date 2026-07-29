# AppleHealthAnalytics
## Especificación Funcional del Sistema

---

# Capítulo 1
## Dominio: Estado General

### Objetivo

Este dominio tiene como propósito responder una pregunta fundamental:

> ¿Cómo se encuentra el usuario actualmente y cómo está evolucionando con respecto a sí mismo?

El análisis no debe limitarse a mostrar valores aislados. Debe interpretar tendencias, comparar periodos, identificar cambios relevantes y generar conclusiones comprensibles.

---

## Información utilizada

Este dominio podrá utilizar información proveniente de:

- Frecuencia cardiaca.
- Variabilidad de la frecuencia cardiaca (HRV).
- Actividad física.
- Entrenamientos.
- Pasos.
- Energía activa.
- Información contextual proveniente del Dominio de Conocimiento Personal.

---

## Indicadores principales

El sistema deberá calcular, entre otros:

- Estado general actual.
- Tendencia de corto plazo.
- Tendencia de mediano plazo.
- Tendencia de largo plazo.
- Nivel de actividad.
- Nivel de recuperación.
- Consistencia.
- Cambios relevantes respecto al periodo anterior.

---

## Preguntas que debe responder

El sistema deberá responder preguntas como:

- ¿Cómo estoy hoy?
- ¿Cómo estoy esta semana?
- ¿Cómo estoy este mes?
- ¿Cómo estoy este año?
- ¿Estoy mejorando?
- ¿Estoy empeorando?
- ¿Cuál ha sido mi evolución?
- ¿Qué cambios importantes ocurrieron recientemente?
- ¿Qué indicadores muestran una tendencia positiva?
- ¿Qué indicadores requieren atención?

---

## Alertas

El sistema podrá generar alertas cuando detecte:

- Cambios bruscos.
- Disminución sostenida de la actividad.
- Disminución de la recuperación.
- Mejoras importantes.
- Periodos largos sin entrenamiento.
- Comportamientos atípicos.

Las alertas deberán incluir una explicación.

Nunca deberán limitarse a indicar que algo cambió.

---

## Recomendaciones

El sistema deberá generar recomendaciones priorizadas.

Cada recomendación deberá incluir:

- motivo;
- evidencia;
- nivel de confianza;
- posible beneficio esperado.

Nunca deberá emitir recomendaciones sin explicar el razonamiento utilizado.

---

## Principios de interpretación

El sistema nunca comparará al usuario con la población general como criterio principal.

La referencia más importante será la evolución histórica del propio usuario.

Las comparaciones con valores poblacionales solamente se utilizarán como contexto adicional cuando sean útiles para interpretar un indicador.

---

## Resultado esperado

Este dominio deberá ser capaz de producir:

- un resumen ejecutivo;
- un diagnóstico general;
- un conjunto de alertas;
- recomendaciones priorizadas;
- respuestas conversacionales relacionadas con el estado general del usuario.

# Capítulo 0
## Filosofía del Sistema

### Misión

AppleHealthAnalytics existe para transformar los datos de Apple Health en conocimiento útil que ayude al usuario a comprender su salud, mejorar su entrenamiento y tomar mejores decisiones.

El sistema no pretende sustituir a un profesional de la salud. Su función es analizar información, detectar patrones, generar hipótesis y ofrecer recomendaciones fundamentadas.

---

### Principios

1. El usuario se compara principalmente consigo mismo.
2. Las tendencias son más importantes que los valores aislados.
3. Toda recomendación debe estar respaldada por evidencia.
4. Toda alerta debe incluir una explicación.
5. El sistema debe reconocer la incertidumbre cuando exista.
6. El contexto personal tiene prioridad sobre las referencias generales.
7. El sistema debe explicar siempre por qué llega a una conclusión.
8. Ningún indicador por sí solo debe determinar una conclusión importante.
9. Las conclusiones deben integrar información de varios dominios.
10. El objetivo del sistema es ayudar al usuario a tomar mejores decisiones, no únicamente mostrar datos.