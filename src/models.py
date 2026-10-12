"""Modelos de datos utilizados por el procesador."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Adjustment:
    """Representa un ajuste de inventario ya separado en columnas."""

    sucursal: str
    turno: str
    cantidad: int
    clave: str
    comentario: str


class AdjustmentFileError(ValueError):
    """Error de formato que impide procesar el archivo completo."""
