"""Пользовательский интерфейс с использованием словарей команд"""
from __future__ import annotations

from typing import Any, Callable, Dict, List

from file_operations import read_objects_from_file, save_objects_to_file
from models import TemperatureMeasurement
from parsers import parse_date_yyyymmdd, parse_float


def print_menu() -> None:
    """Вывести меню"""
    print("\n" + "="*70)
    print("📊 ТЕМПЕРАТУРНЫЙ МОНИТОР".center(70))
    print("="*70)
    print("1. 📋 Просмотреть данные")
    print("2. ➕ Добавить новое измерение")
    print("3. 💾 Сохранить данные в файл")
    print("4. 📂 Загрузить данные из файла")
    print("5. ❌ Выход")
    print("="*70)


def view_data(objects: List[Any]) -> None:
    """Просмотреть все данные"""
    if not objects:
        print("\n❌ Нет данных для отображения!")
        return
    
    print("\n" + "="*70)
    print("📊 АРХИВ ТЕМПЕРАТУРНЫХ ДАННЫХ".center(70))
    print("="*70)
    
    for i, obj in enumerate(objects, 1):
        print(f"  {i}. {obj}")
    
    if objects:
        temps = [obj.value for obj in objects]
        print("\n" + "-"*70)
        print(f"Статистика: Мин={min(temps):.1f}°C | Макс={max(temps):.1f}°C | "
              f"Среднее={sum(temps)/len(temps):.1f}°C")
    print("="*70)


def add_measurement(objects: List[Any]) -> None:
    """Добавить новое измерение"""
    print("\n--- Добавление нового измерения ---")
    try:
        date_str = input("Введите дату (YYYY.MM.DD): ").strip()
        place = input("Введите место: ").strip()
        temp_str = input("Введите температуру (°C): ").strip()
        
        parsed_date = parse_date_yyyymmdd(date_str)
        parsed_temp = parse_float(temp_str)
        
        measurement = TemperatureMeasurement(
            when=parsed_date,
            place=place,
            value=parsed_temp
        )
        objects.append(measurement)
        print(f"✓ Измерение добавлено успешно!")
    except ValueError as e:
        print(f"❌ Ошибка: {e}")


def save_data(objects: List[Any]) -> None:
    """Сохранить данные в файл"""
    save_file = input("Введите имя файла для сохранения: ").strip()
    if save_file:
        try:
            save_objects_to_file(objects, save_file)
            print(f"✓ Данные сохранены в {save_file}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")


def load_data(objects: List[Any]) -> List[Any]:
    """Загрузить данные из файла"""
    load_file = input("Введите имя файла для загрузки: ").strip()
    if load_file:
        try:
            new_objects, errors = read_objects_from_file(load_file)
            
            if errors:
                print(f"\n⚠️  Найдено {len(errors)} ошибок при загрузке:")
                for line_num, error, content in errors[:5]:
                    print(f"  Строка {line_num}: {error}")
                if len(errors) > 5:
                    print(f"  ... и ещё {len(errors) - 5} ошибок")
            
            print(f"✓ Загружено {len(new_objects)} измерений из {load_file}")
            return new_objects
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
    
    return objects


def exit_app() -> None:
    """Выход из приложения"""
    print("✓ Спасибо за использование! До свидания!")


# Словарь команд меню (Command Pattern с использованием словаря)
MENU_COMMANDS: Dict[str, Callable[[List[Any]], Any]] = {
    "1": lambda objs: view_data(objs),
    "2": lambda objs: add_measurement(objs),
    "3": lambda objs: save_data(objs),
    "4": lambda objs: None,  # Требует специальной обработки
    "5": lambda objs: exit_app(),
}


def interactive_mode(input_file: str) -> None:
    """Интерактивный режим с использованием словаря команд"""
    objects, errors = read_objects_from_file(input_file)
    
    if errors:
        print(f"⚠️  Загружено {len(objects)} измерений ({len(errors)} ошибок)")
    else:
        print(f"✓ Загружено {len(objects)} измерений из файла")
    
    print("🚀 Система инициализирована")
    
    while True:
        print_menu()
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "4":
            objects = load_data(objects)
        elif choice == "5":
            exit_app()
            break
        elif choice in MENU_COMMANDS:
            MENU_COMMANDS[choice](objects)
        else:
            print("❌ Неверный выбор! Используйте числа 1-5")
