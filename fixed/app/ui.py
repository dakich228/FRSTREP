"""Console UI for the temperature monitor.

The UI is separated from parsing and file I/O (SRP).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple

from app.file_operations import read_objects_from_file, save_objects_to_file
from app.models import TemperatureMeasurement
from app.parsers import parse_date_yyyymmdd, parse_float

MenuAction = Callable[[List[Any]], List[Any]]


def print_menu() -> None:
    """Print available actions."""
    print("\n" + "=" * 70)
    print("📊 ТЕМПЕРАТУРНЫЙ МОНИТОР".center(70))
    print("=" * 70)
    print("1. 📋 Просмотреть данные")
    print("2. ➕ Добавить новое измерение")
    print("3. 💾 Сохранить данные в файл")
    print("4. 📂 Загрузить данные из файла")
    print("5. ❌ Выход")
    print("=" * 70)


def calc_stats(values: List[float]) -> Tuple[float, float, float]:
    """Return (min, max, avg) for a non-empty list."""
    min_v = min(values)
    max_v = max(values)
    avg_v = sum(values) / len(values)
    return min_v, max_v, avg_v


def view_data(objects: List[Any]) -> List[Any]:
    """Show all measurements."""
    if not objects:
        print("\n❌ Нет данных для отображения!")
        return objects

    print("\n" + "=" * 70)
    print("📊 АРХИВ ТЕМПЕРАТУРНЫХ ДАННЫХ".center(70))
    print("=" * 70)

    for idx, obj in enumerate(objects, 1):
        print(f"  {idx}. {obj}")

    temps = [obj.value for obj in objects]
    min_v, max_v, avg_v = calc_stats(temps)

    print("\n" + "-" * 70)
    print(
        "Статистика: "
        f"Мин={min_v:.1f}°C | Макс={max_v:.1f}°C | Среднее={avg_v:.1f}°C"
    )
    print("=" * 70)
    return objects


def add_measurement(objects: List[Any]) -> List[Any]:
    """Interactively add a new measurement."""
    print("\n--- Добавление нового измерения ---")
    try:
        date_s = input("Введите дату (YYYY.MM.DD): ").strip()
        place = input("Введите место: ").strip()
        temp_s = input("Введите температуру (°C): ").strip()

        parsed_date = parse_date_yyyymmdd(date_s)
        parsed_temp = parse_float(temp_s)

        measurement = TemperatureMeasurement(
            when=parsed_date,
            place=place,
            value=parsed_temp,
        )
        objects.append(measurement)
        print("✓ Измерение добавлено успешно!")
    except ValueError as exc:
        print(f"❌ Ошибка ввода: {exc}")

    return objects


def save_data(objects: List[Any]) -> List[Any]:
    """Ask for filename and save."""
    filename = input("Введите имя файла для сохранения: ").strip()
    if not filename:
        return objects

    save_objects_to_file(objects, filename)
    print(f"✓ Данные сохранены в {filename}")
    return objects


def load_data(objects: List[Any]) -> List[Any]:
    """Ask for filename and load."""
    filename = input("Введите имя файла для загрузки: ").strip()
    if not filename:
        return objects

    new_objects, errors = read_objects_from_file(filename)

    if errors:
        print(f"\n⚠️  Ошибок при загрузке: {len(errors)}")
        for err in errors[:5]:
            print(f"  Строка {err.line_no}: {err.message}")
    print(f"✓ Загружено {len(new_objects)} измерений")
    return new_objects


def exit_app(objects: List[Any]) -> List[Any]:
    """Exit action."""
    print("✓ Спасибо за использование! До свидания!")
    return objects


MENU: Dict[str, MenuAction] = {
    "1": view_data,
    "2": add_measurement,
    "3": save_data,
    "4": load_data,
}


def interactive_mode(input_file: str) -> None:
    """Run the interactive menu."""
    objects, errors = read_objects_from_file(input_file)

    if errors:
        print(f"⚠️  Загружено {len(objects)} измерений ({len(errors)} ошибок)")
    else:
        print(f"✓ Загружено {len(objects)} измерений из файла")

    while True:
        print_menu()
        choice = input("Выберите действие (1-5): ").strip()

        if choice == "5":
            exit_app(objects)
            break

        action = MENU.get(choice)
        if action is None:
            print("❌ Неверный выбор! Используйте числа 1-5")
            continue

        objects = action(objects)
