import os
import tempfile
import unittest
from datetime import date

from app.file_operations import (
    build_object_from_line,
    read_objects_from_file,
    save_objects_to_file,
    tokenize,
)
from app.models import TemperatureMeasurement


class TestTokenize(unittest.TestCase):
    def test_tokenize_simple_line(self):
        tokens = tokenize('temperature 2025.12.31 "Amsterdam" 21.5')
        self.assertEqual(tokens, ['temperature', '2025.12.31', 'Amsterdam', '21.5'])

    def test_tokenize_with_spaces_in_quotes(self):
        tokens = tokenize('temperature 2025.12.31 "Amsterdam Science Park" 21.5')
        self.assertEqual(tokens, ['temperature', '2025.12.31', 'Amsterdam Science Park', '21.5'])


class TestBuildObjectFromLine(unittest.TestCase):
    def test_build_valid(self):
        obj = build_object_from_line('temperature 2025.12.31 "Amsterdam" 21.5')
        self.assertEqual(obj.when, date(2025, 12, 31))
        self.assertEqual(obj.place, "Amsterdam")
        self.assertAlmostEqual(obj.value, 21.5)

    def test_build_mixed_field_order(self):
        obj = build_object_from_line('temperature 7.2 "Rotterdam Center" 2025.12.30')
        self.assertEqual(obj.when, date(2025, 12, 30))
        self.assertEqual(obj.place, "Rotterdam Center")
        self.assertAlmostEqual(obj.value, 7.2)


class TestFileIO(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_read_valid_file(self):
        p = os.path.join(self.test_dir, "data.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write('temperature 2025.12.31 "Amsterdam" 21.5\n')
            f.write('temperature 2025.12.30 "Rotterdam" 7.2\n')

        objs, errors = read_objects_from_file(p)
        self.assertEqual(len(objs), 2)
        self.assertEqual(len(errors), 0)

    def test_read_file_with_errors(self):
        p = os.path.join(self.test_dir, "bad.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write('temperature 2025.12.31 "Amsterdam" 21.5\n')
            f.write('invalid data here\n')

        objs, errors = read_objects_from_file(p)
        self.assertEqual(len(objs), 1)
        self.assertEqual(len(errors), 1)

    def test_save_objects_to_file(self):
        p = os.path.join(self.test_dir, "out.txt")
        objs = [TemperatureMeasurement(date(2025, 12, 31), "Amsterdam", 21.5)]
        save_objects_to_file(objs, p)
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("2025.12.31", content)
        self.assertIn("Amsterdam", content)
        self.assertIn("21,5", content)


if __name__ == "__main__":
    unittest.main()
