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


class TestParsers(unittest.TestCase):
    def test_date_ok(self):
        self.assertEqual(parse_date_yyyymmdd("2025.12.31"), date(2025, 12, 31))

    def test_date_bad(self):
        with self.assertRaises(ValueError):
            parse_date_yyyymmdd("31-12-2025")

    def test_time_ok(self):
        self.assertEqual(parse_time_hhmm("14:30"), time(14, 30))

    def test_time_bad(self):
        with self.assertRaises(ValueError):
            parse_time_hhmm("99:99")

    def test_int_ok(self):
        self.assertEqual(parse_int("-42"), -42)

    def test_int_bad(self):
        with self.assertRaises(ValueError):
            parse_int("3.14")

    def test_float_ok(self):
        self.assertEqual(parse_float("3,14"), 3.14)

    def test_float_bad(self):
        with self.assertRaises(ValueError):
            parse_float("abc")

    def test_str_ok(self):
        self.assertEqual(parse_str("Amsterdam"), "Amsterdam")

    def test_try_parse_unknown(self):
        ok, value = try_parse("x", "unknown")
        self.assertFalse(ok)
        self.assertIsNone(value)


if __name__ == "__main__":
    unittest.main()
