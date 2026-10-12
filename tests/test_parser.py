"""Pruebas unitarias del análisis de ajustes.txt."""

import unittest

from src.models import AdjustmentFileError
from src.parser import parse_adjustments


class ParseAdjustmentsTests(unittest.TestCase):
    def test_parses_adjustments_in_original_order(self):
        lines = [
            "SPT1\n",
            "0001-10 CONSUMO PERSONAL\n",
            "0127+5 UNO POR OTRO\n",
            "\n",
            "SPT2\n",
            "C1T1\n",
            "1+2 ERROR EN EL TRASPASO\n",
            "PAT2\n",
            "1-1 CONSUMO\n",
        ]

        result = parse_adjustments(lines)

        self.assertEqual(len(result), 4)
        self.assertEqual(
            [(x.sucursal, x.turno, x.cantidad, x.clave, x.comentario) for x in result],
            [
                ("SP", "T1", -10, "0001", "CONSUMO PERSONAL"),
                ("SP", "T1", 5, "0127", "UNO POR OTRO"),
                ("C1", "T1", 2, "1", "ERROR EN EL TRASPASO"),
                ("PA", "T2", -1, "1", "CONSUMO"),
            ],
        )

    def test_empty_sections_return_no_adjustments(self):
        self.assertEqual(parse_adjustments(["SPT1\n", "\n", "C1T2\n"]), [])

    def test_internal_comment_spaces_are_preserved(self):
        result = parse_adjustments(["SPT1\n", "7+3 ERROR  EN EL TRASPASO\n"])
        self.assertEqual(result[0].comentario, "ERROR  EN EL TRASPASO")

    def test_malformed_line_reports_line_number(self):
        with self.assertRaisesRegex(AdjustmentFileError, "línea 2"):
            parse_adjustments(["SPT1\n", "esto no es un ajuste\n"])

    def test_adjustment_before_header_is_rejected(self):
        with self.assertRaisesRegex(AdjustmentFileError, "antes del primer encabezado"):
            parse_adjustments(["1+2 CONSUMO\n"])


if __name__ == "__main__":
    unittest.main()
