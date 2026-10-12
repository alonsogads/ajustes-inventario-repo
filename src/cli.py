"""Interfaz de línea de comandos del programa."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .exporter import export_adjustments
from .models import AdjustmentFileError
from .parser import read_adjustments_file


def _application_directory() -> Path:
    """Directorio del ejecutable o, al ejecutar desde código, del proyecto."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="AjustesInventario",
        description=(
            "Lee los ajustes por sucursal y turno de ajustes.txt y los exporta "
            "a una tabla ordenada en Excel o CSV."
        ),
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        help="Archivo de entrada. Por omisión, ajustes.txt junto al programa.",
    )
    parser.add_argument(
        "-o",
        "--salida",
        help=(
            "Ruta de salida. Por omisión, ajustes_procesados.xlsx junto al archivo "
            "de entrada. La extensión .xlsx o .csv selecciona el formato."
        ),
    )
    parser.add_argument("--version", action="version", version=f"AjustesInventario {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    app_dir = _application_directory()
    input_path = (
        Path(args.archivo).expanduser().resolve()
        if args.archivo
        else (app_dir / "ajustes.txt").resolve()
    )

    if not input_path.exists():
        print(
            f"Error: no se encontró el archivo de entrada:\n  {input_path}\n\n"
            "Coloca ajustes.txt junto al programa o indica su ruta como argumento.",
            file=sys.stderr,
        )
        return 2
    if not input_path.is_file():
        print(f"Error: la ruta no es un archivo: {input_path}", file=sys.stderr)
        return 2

    if args.salida:
        output_path = Path(args.salida).expanduser().resolve()
    else:
        output_path = input_path.parent / "ajustes_procesados.xlsx"

    if output_path == input_path:
        print("Error: el archivo de salida no puede ser el mismo que el archivo de entrada.", file=sys.stderr)
        return 2

    try:
        adjustments = read_adjustments_file(str(input_path))
        if not adjustments:
            print(
                "No se encontraron ajustes. No se generó ni modificó ningún archivo de salida."
            )
            return 0

        saved_path = export_adjustments(adjustments, output_path)
    except (OSError, AdjustmentFileError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Ajustes encontrados: {len(adjustments)}")
    print(f"Archivo generado: {saved_path}")
    return 0
