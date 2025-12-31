"""Тесты для парсеров"""
import unittest
from datetime import date, time

from parsers import (
    parse_date_yyyymmdd,
    parse_time_hhmm,
    parse_int,
    parse_float,
    parse_str,
    try_parse,
)


class TestDateParser(unittest.TestCase):
    """Тесты для парсинга дат"""

    def test_valid_date(self):
        """Парсинг валидной даты"""
        result = parse_date_yyyymmdd("2025.12.31")
        self.assertEqual(result, date(2025, 12, 31))

    def test_valid_date_beginning_of_year(self):
        """Парсинг даты в начале года"""
        result = parse_date_yyyymmdd("2024.01.01")
        self.assertEqual(result, date(2024, 1, 1))

    def test_invalid_date_wrong_format(self):
        """Ошибка при неправильном формате даты"""
        with self.assertRaises(ValueError):
            parse_date_yyyymmdd("31-12-2025")

    def test_invalid_date_month_out_of_range(self):
        """Ошибка при месяце больше 12"""
        with self.assertRaises(ValueError):
            parse_date_yyyymmdd("2025.13.01")

    def test_invalid_date_day_out_of_range(self):
        """Ошибка при дне больше 31"""
        with self.assertRaises(ValueError):
            parse_date_yyyymmdd("2025.12.32")

    def test_invalid_date_leap_year(self):
        """Ошибка при невалидной дате в невисокосном году"""
        with self.assertRaises(ValueError):
            parse_date_yyyymmdd("2023.02.29")


class TestTimeParser(unittest.TestCase):
    """Тесты для парсинга времени"""

    def test_valid_time(self):
        """Парсинг валидного времени"""
        result = parse_time_hhmm("14:30")
        self.assertEqual(result, time(14, 30))

    def test_valid_time_midnight(self):
        """Парсинг полуночи"""
        result = parse_time_hhmm("00:00")
        self.assertEqual(result, time(0, 0))

    def test_valid_time_end_of_day(self):
        """Парсинг конца дня"""
        result = parse_time_hhmm("23:59")
        self.assertEqual(result, time(23, 59))

    def test_invalid_time_wrong_format(self):
        """Ошибка при неправильном формате времени"""
        with self.assertRaises(ValueError):
            parse_time_hhmm("14-30")

    def test_invalid_time_hour_out_of_range(self):
        """Ошибка при часе больше 23"""
        with self.assertRaises(ValueError):
            parse_time_hhmm("25:00")

    def test_invalid_time_minute_out_of_range(self):
        """Ошибка при минуте больше 59"""
        with self.assertRaises(ValueError):
            parse_time_hhmm("14:60")


class TestIntParser(unittest.TestCase):
    """Тесты для парсинга целых чисел"""

    def test_valid_positive_int(self):
        """Парсинг положительного числа"""
        self.assertEqual(parse_int("42"), 42)

    def test_valid_negative_int(self):
        """Парсинг отрицательного числа"""
        self.assertEqual(parse_int("-42"), -42)

    def test_valid_zero(self):
        """Парсинг нуля"""
        self.assertEqual(parse_int("0"), 0)

    def test_valid_plus_sign(self):
        """Парсинг числа с плюсом"""
        self.assertEqual(parse_int("+42"), 42)

    def test_invalid_float_format(self):
        """Ошибка при парсинге дробного числа"""
        with self.assertRaises(ValueError):
            parse_int("3.14")

    def test_invalid_non_numeric(self):
        """Ошибка при парсинге текста"""
        with self.assertRaises(ValueError):
            parse_int("abc")


class TestFloatParser(unittest.TestCase):
    """Тесты для парсинга чисел с плавающей точкой"""

    def test_valid_float_with_dot(self):
        """Парсинг числа с точкой"""
        self.assertEqual(parse_float("3.14"), 3.14)

    def test_valid_float_with_comma(self):
        """Парсинг числа с запятой (европейский формат)"""
        self.assertEqual(parse_float("3,14"), 3.14)

    def test_valid_negative_float(self):
        """Парсинг отрицательного дробного числа"""
        self.assertEqual(parse_float("-2.5"), -2.5)

    def test_valid_positive_float_sign(self):
        """Парсинг положительного дробного числа с плюсом"""
        self.assertEqual(parse_float("+5.5"), 5.5)

    def test_valid_integer_as_float(self):
        """Парсинг целого числа как float"""
        self.assertEqual(parse_float("42"), 42.0)

    def test_valid_temperature_values(self):
        """Парсинг реальных температурных значений"""
        self.assertEqual(parse_float("21.5"), 21.5)
        self.assertEqual(parse_float("-4,6"), -4.6)
        self.assertEqual(parse_float("+12.0"), 12.0)

    def test_invalid_multiple_dots(self):
        """Ошибка при множественных точках"""
        with self.assertRaises(ValueError):
            parse_float("3.14.15")

    def test_invalid_non_numeric(self):
        """Ошибка при парсинге текста"""
        with self.assertRaises(ValueError):
            parse_float("abc")


class TestStrParser(unittest.TestCase):
    """Тесты для парсинга строк"""

    def test_valid_string(self):
        """Парсинг строки"""
        self.assertEqual(parse_str("Amsterdam"), "Amsterdam")

    def test_string_with_numbers(self):
        """Парсинг строки с числами"""
        self.assertEqual(parse_str("Amsterdam123"), "Amsterdam123")

    def test_empty_string(self):
        """Парсинг пустой строки"""
        self.assertEqual(parse_str(""), "")


class TestTryParse(unittest.TestCase):
    """Тесты для функции try_parse"""

    def test_try_parse_valid_date(self):
        """Успешный парсинг даты"""
        success, value = try_parse("2025.12.31", "date")
        self.assertTrue(success)
        self.assertEqual(value, date(2025, 12, 31))

    def test_try_parse_invalid_date(self):
        """Неудачный парсинг даты"""
        success, value = try_parse("invalid", "date")
        self.assertFalse(success)
        self.assertIsNone(value)

    def test_try_parse_valid_float(self):
        """Успешный парсинг float"""
        success, value = try_parse("3.14", "float")
        self.assertTrue(success)
        self.assertEqual(value, 3.14)

    def test_try_parse_invalid_float(self):
        """Неудачный парсинг float"""
        success, value = try_parse("not_a_number", "float")
        self.assertFalse(success)
        self.assertIsNone(value)

    def test_try_parse_valid_int(self):
        """Успешный парсинг int"""
        success, value = try_parse("42", "int")
        self.assertTrue(success)
        self.assertEqual(value, 42)

    def test_try_parse_invalid_int(self):
        """Неудачный парсинг int"""
        success, value = try_parse("3.14", "int")
        self.assertFalse(success)
        self.assertIsNone(value)

    def test_try_parse_unknown_type(self):
        """Неудачный парсинг для неизвестного типа"""
        success, value = try_parse("something", "unknown_type")
        self.assertFalse(success)
        self.assertIsNone(value)

    def test_try_parse_str(self):
        """Парсинг строки всегда успешен"""
        success, value = try_parse("anything", "str")
        self.assertTrue(success)
        self.assertEqual(value, "anything")


if __name__ == "__main__":
    unittest.main()
