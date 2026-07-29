"""Modelo de dominio para entrenamientos de Apple Health."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WorkoutRecord:
    """Representa una sesión de actividad física realizada por el usuario.

    Constituye un evento dentro del historial de salud, independiente del
    formato XML de Apple Health, y puede asociarse con múltiples registros
    de salud ocurridos durante su intervalo temporal.
    """

    identificador: str | None = None
    """Identificador único del entrenamiento dentro del repositorio de salud."""

    tipo_actividad: str | None = None
    """Tipo de actividad física realizada durante la sesión."""

    fecha_inicio: datetime | None = None
    """Momento en que comienza el entrenamiento."""

    fecha_fin: datetime | None = None
    """Momento en que finaliza el entrenamiento."""

    fecha_creacion: datetime | None = None
    """Momento en que el registro fue creado en la fuente de origen."""

    fecha_modificacion: datetime | None = None
    """Momento en que el registro fue modificado por última vez en la fuente."""

    duracion: float | None = None
    """Duración total de la sesión de entrenamiento."""

    unidad_duracion: str | None = None
    """Unidad en la que se expresa la duración."""

    distancia_total: float | None = None
    """Distancia recorrida durante el entrenamiento, cuando aplica."""

    unidad_distancia: str | None = None
    """Unidad en la que se expresa la distancia total."""

    energia_total: float | None = None
    """Energía consumida durante el entrenamiento, cuando aplica."""

    unidad_energia: str | None = None
    """Unidad en la que se expresa la energía total."""

    fuente_origen: str | None = None
    """Aplicación o servicio que originó el registro del entrenamiento."""

    dispositivo: str | None = None
    """Dispositivo que registró la sesión de entrenamiento, cuando aplica."""

    metadatos: dict[str, Any] = field(default_factory=dict)
    """Información adicional asociada al entrenamiento que no forma parte del núcleo."""
