import csv
import io
import unittest

from src.charts import distribution_chart, probability_chart
from src.utils import EMOTIONS, clean_texts, csv_bytes, read_csv, results_table


class CsvTests(unittest.TestCase):
    def test_column_selection_and_blank_rows(self):
        for sep in (",", ";", "\t"):
            with self.subTest(separator=sep):
                data = read_csv(
                    f'id{sep}frase\n1{sep}"¡Qué alegría!\nVolví."\n\n2{sep} \n'
                    .encode("utf-8-sig")
                )
                self.assertEqual(clean_texts(data["frase"]), (["¡Qué alegría!\nVolví."], 2))

    def test_invalid_formats(self):
        for content in (b"", b"\xff", b"col\n", b"a,a\nx,y", b"a,b\nx,y,z", b'a\n"x'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                read_csv(content)

    def test_export_preserves_accents_and_escapes_formulas(self):
        probabilities = dict.fromkeys(EMOTIONS, 0)
        probabilities["Alegría"] = 1
        table = results_table([{
            "text": "=¡Qué alegría!", "emotion": "Alegría", "confidence": 1,
            "probabilities": probabilities,
        }])
        content = csv_bytes(table)
        self.assertTrue(content.startswith(b"\xef\xbb\xbf"))
        row, = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        self.assertEqual(row["Texto"], "'=¡Qué alegría!")
        self.assertEqual(row["Emoción"], "Alegría")
        self.assertEqual(table.at[0, "Texto"], "=¡Qué alegría!")

    def test_charts_show_six_ordered_values(self):
        scores = dict(zip(EMOTIONS, [0.1, 0.2, 0.05, 0.3, 0.25, 0.1], strict=True))
        chart = probability_chart({"probabilities": scores})
        self.assertEqual(list(chart.data[0].x), sorted(scores.values(), reverse=True))
        self.assertEqual(chart.layout.yaxis.autorange, "reversed")
        distribution = distribution_chart([{"emotion": "Ira"}, {"emotion": "Ira"}, {"emotion": "Miedo"}])
        self.assertEqual(list(distribution.data[0].customdata), [2, 1, 0, 0, 0, 0])
