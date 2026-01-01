import unittest
from datetime import date, time

from app.parsers import (
    parse_date_yyyymmdd,
    parse_time_hhmm,
    parse_int,
    parse_float,
    parse_str,
    try_parse,
)


class TestDateParser(unittest.TestCase):
    def test_valid_date(self):
        self.assertEqual(parse_date_yyyymmdd("2025.12.31"), date(2025, 12, 31))

    def test_invalid_date_wrong_format(self):
        with self.assertRaises(ValueError):
            parse_date_yyyymmdd("31-12-2025")


class TestTimeParser(unittest.TestCase):
    def test_valid_time(self):
        self.assertEqual(parse_time_hhmm("14:30"), time(14, 30))

    def test_invalid_time(self):
        with self.assertRaises(ValueError):
            parse_time_hhmm("99:99")


class TestIntParser(unittest.TestCase):
    def test_valid_int(self):
        self.assertEqual(parse_int("-42"), -42)

    def test_invalid_int(self):
        with self.assertRaises(ValueError):
            parse_int("3.14")


class TestFloatParser(unittest.TestCase):
    def test_valid_float(self):
        self.assertEqual(parse_float("3,14"), 3.14)

    def test_invalid_float(self):
        with self.assertRaises(ValueError):
            parse_float("abc")


class TestTryParse(unittest.TestCase):
    def test_try_parse_valid_date(self):
        ok, value = try_parse("2025.12.31", "date")
        self.assertTrue(ok)
        self.assertEqual(value, date(2025, 12, 31))

    def test_try_parse_unknown_type(self):
        ok, value = try_parse("x", "unknown")
        self.assertFalse(ok)
        self.assertIsNone(value)


class TestStrParser(unittest.TestCase):
    def test_str(self):
        self.assertEqual(parse_str("Amsterdam"), "Amsterdam")


if __name__ == "__main__":
    unittest.main()
