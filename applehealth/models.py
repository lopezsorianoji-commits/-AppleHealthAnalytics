"""Modelos de dominio para AppleHealthAnalytics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class HealthRecord:
    """Representa una observación o medición individual de salud.

    Constituye la entidad base del dominio de salud y es independiente
    del origen de los datos. Todos los registros especializados derivan
    conceptualmente de esta entidad.
    """

    identificador: str | None = None
    """Identificador único del registro dentro del repositorio de salud."""

    tipo_registro: str | None = None
    """Tipo de registro que clasifica la observación o medición."""

    fecha_inicio: datetime | None = None
    """Momento en que comienza el intervalo al que corresponde la medición."""

    fecha_fin: datetime | None = None
    """Momento en que finaliza el intervalo al que corresponde la medición."""

    fecha_creacion: datetime | None = None
    """Momento en que el registro fue creado en la fuente de origen."""

    fecha_modificacion: datetime | None = None
    """Momento en que el registro fue modificado por última vez en la fuente."""

    fuente_origen: str | None = None
    """Aplicación o servicio que originó el registro."""

    dispositivo: str | None = None
    """Dispositivo que capturó o generó la medición, cuando aplica."""

    unidad_medida: str | None = None
    """Unidad en la que se expresa el valor de la medición."""

    valor: float | None = None
    """Magnitud numérica de la observación o medición."""

    metadatos: dict[str, Any] = field(default_factory=dict)
    """Información adicional asociada al registro que no forma parte del núcleo."""
