import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from unittest.mock import patch

from app.models import TemperatureMeasurement
from app.ui import exit_app, interactive_mode, load_data, save_data, view_data


class TestUi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def test_view_data_prints_stats(self):
        objs = [
            TemperatureMeasurement(date(2025, 12, 31), "Amsterdam", 21.5),
            TemperatureMeasurement(date(2025, 12, 30), "Rotterdam", 7.2),
        ]
        buf = io.StringIO()
        with redirect_stdout(buf):
            view_data(objs)
        out = buf.getvalue()
        self.assertIn("Amsterdam", out)
        self.assertIn("Статистика", out)

    def test_save_data_writes_file(self):
        p = os.path.join(self.tmp, "out.txt")
        objs = [TemperatureMeasurement(date(2025, 12, 31), "Amsterdam", 21.5)]
        with patch("builtins.input", return_value=p):
            buf = io.StringIO()
            with redirect_stdout(buf):
                save_data(objs)
        self.assertTrue(os.path.exists(p))

    def test_load_data_reads_file(self):
        p = os.path.join(self.tmp, "in.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write('temperature 2025.12.31 "Amsterdam" 21.5\n')

        with patch("builtins.input", return_value=p):
            buf = io.StringIO()
            with redirect_stdout(buf):
                new_objs = load_data([])
        self.assertEqual(len(new_objs), 1)
        self.assertEqual(new_objs[0].place, "Amsterdam")

    def test_exit_app_prints_message(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_app([])
        self.assertIn("До свидания", buf.getvalue())

    def test_interactive_mode_invalid_choice(self):
        input_file = os.path.join(self.tmp, "data.txt")
        with open(input_file, "w", encoding="utf-8") as f:
            f.write('temperature 2025.12.31 "Amsterdam" 21.5\n')

        # 999 -> invalid menu option, 5 -> exit
        with patch("builtins.input", side_effect=["999", "5"]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                interactive_mode(input_file)
        self.assertIn("Неверный выбор", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
