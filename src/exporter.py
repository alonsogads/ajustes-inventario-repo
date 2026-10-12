"""Exportación de los ajustes a Excel (.xlsx) o CSV (.csv)."""

from __future__ import annotations

import csv
from pathlib import Path
from collections.abc import Sequence

from .models import Adjustment

COLUMNS = ["Sucursal", "Turno", "Cantidad", "Clave", "Comentario"]


def export_adjustments(adjustments: Sequence[Adjustment], output_path: str | Path) -> Path:
    """Exporta los ajustes según la extensión del archivo de salida.

    .xlsx crea un libro de Excel con una tabla y conserva Clave como texto.
    .csv crea un CSV separado por punto y coma, con codificación UTF-8 con BOM.
    """
    path = Path(output_path).expanduser().resolve()
    extension = path.suffix.lower()

    if extension == ".xlsx":
        _export_xlsx(adjustments, path)
    elif extension == ".csv":
        _export_csv(adjustments, path)
    else:
        raise ValueError(
            "El formato de salida debe ser .xlsx o .csv; por ejemplo, ajustes_procesados.xlsx."
        )

    return path


def _rows(adjustments: Sequence[Adjustment]):
    for item in adjustments:
        yield [item.sucursal, item.turno, item.cantidad, item.clave, item.comentario]


def _export_csv(adjustments: Sequence[Adjustment], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file, delimiter=";", lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(_rows(adjustments))


def _export_xlsx(adjustments: Sequence[Adjustment], path: Path) -> None:
    try:
        from openpyxl import Workbook
        from openpyxl.worksheet.table import Table, TableStyleInfo
    except ImportError as error:
        raise RuntimeError(
            "Para exportar a Excel (.xlsx), instala las dependencias con: "
            "python -m pip install -r requirements.txt"
        ) from error

    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Ajustes"
    worksheet.append(COLUMNS)

    for row in _rows(adjustments):
        worksheet.append(row)

    # Asegura que claves como 0001 y 0127 se conserven como texto en Excel.
    for cell in worksheet["D"][1:]:
        cell.number_format = "@"

    worksheet.freeze_panes = "A2"
    worksheet.sheet_view.showGridLines = False
    worksheet.auto_filter.ref = worksheet.dimensions

    # Crear una tabla de Excel facilita filtrar y ordenar los ajustes.
    table = Table(displayName="TablaAjustes", ref=worksheet.dimensions)
    table_style = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    table.tableStyleInfo = table_style
    worksheet.add_table(table)

    widths = {"A": 14, "B": 10, "C": 12, "D": 14, "E": 40}
    for column, width in widths.items():
        worksheet.column_dimensions[column].width = width

    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
