"""Тесты для работы с файлами и токенизацией"""
import os
import tempfile
import unittest
from datetime import date

from file_operations import tokenize, build_object_from_line, read_objects_from_file, save_objects_to_file
from models import TemperatureMeasurement


class TestTokenize(unittest.TestCase):
    """Тесты для функции tokenize"""

    def test_tokenize_simple_line(self):
        """Разбиение простой строки"""
        tokens = tokenize('temperature 2025.12.31 "Amsterdam" 21.5')
        self.assertEqual(tokens, ['temperature', '2025.12.31', 'Amsterdam', '21.5'])

    def test_tokenize_with_spaces_in_quotes(self):
        """Разбиение строки с пробелами в кавычках"""
        tokens = tokenize('temperature 2025.12.31 "Amsterdam Science Park" 21.5')
        self.assertEqual(tokens, ['temperature', '2025.12.31', 'Amsterdam Science Park', '21.5'])

    def test_tokenize_multiple_quoted_strings(self):
        """Разбиение со множественными кавычками"""
        tokens = tokenize('cmd "first arg" "second arg"')
        self.assertEqual(tokens, ['cmd', 'first arg', 'second arg'])

    def test_tokenize_empty_string(self):
        """Разбиение пустой строки"""
        tokens = tokenize('')
        self.assertEqual(tokens, [])

    def test_tokenize_only_spaces(self):
        """Разбиение строки только с пробелами"""
        tokens = tokenize('   ')
        self.assertEqual(tokens, [])

    def test_tokenize_no_quotes(self):
        """Разбиение строки без кавычек"""
        tokens = tokenize('word1 word2 word3')
        self.assertEqual(tokens, ['word1', 'word2', 'word3'])


class TestBuildObjectFromLine(unittest.TestCase):
    """Тесты для функции build_object_from_line"""

    def test_build_valid_temperature_measurement(self):
        """Построение валидного объекта температуры"""
        line = 'temperature 2025.12.31 "Amsterdam" 21.5'
        obj = build_object_from_line(line)
        
        self.assertIsInstance(obj, TemperatureMeasurement)
        self.assertEqual(obj.when, date(2025, 12, 31))
        self.assertEqual(obj.place, "Amsterdam")
        self.assertEqual(obj.value, 21.5)

    def test_build_negative_temperature(self):
        """Построение объекта с отрицательной температурой"""
        line = 'temperature 2025.01.05 "Groningen" -4.6'
        obj = build_object_from_line(line)
        self.assertEqual(obj.value, -4.6)

    def test_build_with_comma_separator(self):
        """Построение объекта с запятой как разделитель"""
        line = 'temperature 2025.11.15 "Utrecht" 3,8'
        obj = build_object_from_line(line)
        self.assertEqual(obj.value, 3.8)

    def test_build_mixed_field_order_date_place_value(self):
        """Построение с правильным порядком полей"""
        line = 'temperature 2025.12.30 "Rotterdam" 7.2'
        obj = build_object_from_line(line)
        self.assertEqual(obj.place, "Rotterdam")

    def test_build_mixed_field_order_value_place_date(self):
        """Построение с перепутанным порядком (значение, место, дата)"""
        line = 'temperature 7.2 "Rotterdam Center" 2025.12.30'
        obj = build_object_from_line(line)
        self.assertEqual(obj.when, date(2025, 12, 30))
        self.assertEqual(obj.place, "Rotterdam Center")
        self.assertEqual(obj.value, 7.2)

    def test_build_empty_line(self):
        """Ошибка при пустой строке"""
        with self.assertRaises(ValueError):
            build_object_from_line('')

    def test_build_unknown_type(self):
        """Ошибка при неизвестном типе"""
        with self.assertRaises(ValueError):
            build_object_from_line('unknown 2025.12.31 "Place" 10')

    def test_build_wrong_number_of_properties(self):
        """Ошибка при неправильном числе свойств"""
        with self.assertRaises(ValueError):
            build_object_from_line('temperature 2025.12.31 "Place"')

    def test_build_invalid_date(self):
        """Ошибка при невалидной дате"""
        with self.assertRaises(ValueError):
            build_object_from_line('temperature invalid_date "Place" 20.0')

    def test_build_invalid_temperature_value(self):
        """Ошибка при невалидном значении температуры"""
        with self.assertRaises(ValueError):
            build_object_from_line('temperature 2025.12.31 "Place" not_a_number')


class TestFileOperations(unittest.TestCase):
    """Тесты для работы с файлами"""

    def setUp(self):
        """Подготовка тестового окружения"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_read_valid_file(self):
        """Чтение валидного файла"""
        # Создаем тестовый файл
        test_file = os.path.join(self.test_dir, "test_data.txt")
        with open(test_file, "w") as f:
            f.write('temperature 2025.12.31 "Amsterdam" 21.5\n')
            f.write('temperature 2025.12.30 "Rotterdam" 7.2\n')
        
        objects, errors = read_objects_from_file(test_file)
        self.assertEqual(len(objects), 2)
        self.assertEqual(len(errors), 0)

    def test_read_file_with_errors(self):
        """Чтение файла с ошибками"""
        test_file = os.path.join(self.test_dir, "test_data_errors.txt")
        with open(test_file, "w") as f:
            f.write('temperature 2025.12.31 "Amsterdam" 21.5\n')
            f.write('invalid data here\n')
            f.write('temperature 2025.12.30 "Rotterdam" 7.2\n')
        
        objects, errors = read_objects_from_file(test_file)
        self.assertEqual(len(objects), 2)
        self.assertEqual(len(errors), 1)

    def test_read_empty_file(self):
        """Чтение пустого файла"""
        test_file = os.path.join(self.test_dir, "empty.txt")
        with open(test_file, "w") as f:
            pass
        
        objects, errors = read_objects_from_file(test_file)
        self.assertEqual(len(objects), 0)
        self.assertEqual(len(errors), 0)

    def test_save_objects_to_file(self):
        """Сохранение объектов в файл"""
        test_file = os.path.join(self.test_dir, "output.txt")
        
        objects = [
            TemperatureMeasurement(date(2025, 12, 31), "Amsterdam", 21.5),
            TemperatureMeasurement(date(2025, 12, 30), "Rotterdam", 7.2),
        ]
        
        save_objects_to_file(objects, test_file)
        
        self.assertTrue(os.path.exists(test_file))
        
        with open(test_file, "r") as f:
            content = f.read()
        
        self.assertIn("2025.12.31", content)
        self.assertIn("Amsterdam", content)
        self.assertIn("21,5", content)

    def test_roundtrip_save_and_load(self):
        """Полный цикл сохранения и загрузки"""
        test_file = os.path.join(self.test_dir, "roundtrip.txt")
        
        original = [
            TemperatureMeasurement(date(2025, 12, 31), "Amsterdam", 21.5),
            TemperatureMeasurement(date(2024, 1, 1), "Berlin", -5.3),
        ]
        
        save_objects_to_file(original, test_file)
        loaded, errors = read_objects_from_file(test_file)
        
        self.assertEqual(len(loaded), len(original))
        self.assertEqual(len(errors), 0)
        
        for orig, load in zip(original, loaded):
            self.assertEqual(orig.when, load.when)
            self.assertEqual(orig.place, load.place)
            self.assertAlmostEqual(orig.value, load.value, places=1)


class TestTemperatureMeasurement(unittest.TestCase):
    """Тесты для класса TemperatureMeasurement"""

    def test_create_measurement(self):
        """Создание объекта измерения"""
        measurement = TemperatureMeasurement(
            date(2025, 12, 31),
            "Amsterdam",
            21.5
        )
        self.assertEqual(measurement.when, date(2025, 12, 31))
        self.assertEqual(measurement.place, "Amsterdam")
        self.assertEqual(measurement.value, 21.5)

    def test_measurement_is_frozen(self):
        """Проверка неизменяемости объекта"""
        measurement = TemperatureMeasurement(
            date(2025, 12, 31),
            "Amsterdam",
            21.5
        )
        with self.assertRaises(Exception):
            measurement.value = 25.0

    def test_measurement_string_representation(self):
        """Проверка строкового представления"""
        measurement = TemperatureMeasurement(
            date(2025, 12, 31),
            "Amsterdam",
            21.5
        )
        string = str(measurement)
        self.assertIn("31.12.2025", string)
        self.assertIn("Amsterdam", string)
        self.assertIn("+21.5", string)


if __name__ == "__main__":
    unittest.main()
