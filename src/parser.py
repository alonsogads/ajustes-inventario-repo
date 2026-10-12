"""Lectura y análisis del formato de ajustes.txt."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .models import Adjustment, AdjustmentFileError

# Ejemplos válidos: SPT1, C1T2, PAT1.
_HEADER_RE = re.compile(r"^(?P<sucursal>\S{2})T(?P<turno>[12])$")

# Ejemplos válidos: 0001-10 CONSUMO PERSONAL, 0127+5 UNO POR OTRO, 1-1 CONSUMO.
# La clave se conserva como texto para no perder ceros a la izquierda.
_ADJUSTMENT_RE = re.compile(
    r"^(?P<clave>\d+)(?P<signo>[+-])(?P<cantidad>\d+)"
    r"(?:[ \t]+(?P<comentario>.*))?$"
)


def parse_adjustments(lines: Iterable[str]) -> list[Adjustment]:
    """Convierte las líneas del archivo en ajustes ordenados.

    Las líneas vacías se ignoran. Cada ajuste debe pertenecer a una sección
    identificada por un encabezado como SPT1 o C1T2. Si se encuentra una línea
    no vacía que no cumple el formato, se genera un error con su número de línea
    para evitar exportar una tabla incompleta silenciosamente.
    """
    adjustments: list[Adjustment] = []
    current_sucursal: str | None = None
    current_turno: str | None = None

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue

        header_match = _HEADER_RE.fullmatch(line)
        if header_match:
            current_sucursal = header_match.group("sucursal")
            current_turno = f"T{header_match.group('turno')}"
            continue

        adjustment_match = _ADJUSTMENT_RE.fullmatch(line)
        if not adjustment_match:
            raise AdjustmentFileError(
                f"La línea {line_number} no tiene un formato reconocido: {raw_line.rstrip()!r}"
            )

        if current_sucursal is None or current_turno is None:
            raise AdjustmentFileError(
                f"La línea {line_number} contiene un ajuste antes del primer encabezado de sucursal/turno."
            )

        magnitude = int(adjustment_match.group("cantidad"))
        if adjustment_match.group("signo") == "-":
            magnitude *= -1

        adjustments.append(
            Adjustment(
                sucursal=current_sucursal,
                turno=current_turno,
                cantidad=magnitude,
                clave=adjustment_match.group("clave"),
                comentario=(adjustment_match.group("comentario") or "").strip(),
            )
        )

    return adjustments


def read_adjustments_file(path: str) -> list[Adjustment]:
    """Lee ajustes.txt (UTF-8 o, como alternativa, Windows-1252) y lo analiza."""
    from pathlib import Path

    file_path = Path(path)
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        # Permite archivos de texto creados con la codificación tradicional de Windows.
        content = file_path.read_text(encoding="cp1252")
    except OSError as error:
        raise OSError(f"No se pudo leer el archivo {file_path}: {error}") from error

    return parse_adjustments(content.splitlines())
