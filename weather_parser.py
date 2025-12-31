from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
import re
import sys
from typing import Any, Callable, Dict, List, Sequence, Tuple


TOKEN_RE = re.compile(r'"([^"]*)"|(\S+)')
RE_DATE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
RE_TIME = re.compile(r"^\d{2}:\d{2}$")
RE_INT = re.compile(r"^[+-]?\d+$")
RE_FLOAT = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


@dataclass(frozen=True)
class TemperatureMeasurement:
    when: date
    place: str
    value: float


def tokenize(line: str) -> List[str]:
    return [q if q else b for q, b in TOKEN_RE.findall(line)]


def parse_date_yyyymmdd(token: str) -> date:
    if not RE_DATE.match(token):
        raise ValueError(f"Invalid date: {token}")
    return datetime.strptime(token, "%Y.%m.%d").date()


def parse_time_hhmm(token: str) -> time:
    if not RE_TIME.match(token):
        raise ValueError(f"Invalid time: {token}")
    return datetime.strptime(token, "%H:%M").time()


def parse_int(token: str) -> int:
    if not RE_INT.match(token):
        raise ValueError(f"Invalid int: {token}")
    return int(token)


def parse_float(token: str) -> float:
    if not RE_FLOAT.match(token):
        raise ValueError(f"Invalid float: {token}")
    return float(token.replace(",", "."))


def parse_str(token: str) -> str:
    return token


TYPE_PARSERS: Dict[str, Callable[[str], Any]] = {
    "date": parse_date_yyyymmdd,
    "time": parse_time_hhmm,
    "int": parse_int,
    "float": parse_float,
    "str": parse_str,
}

FieldSpec = Tuple[str, str]
SchemaSpec = Tuple[type, Sequence[FieldSpec]]

OBJECT_SCHEMAS: Dict[str, SchemaSpec] = {
    "temperature": (
        TemperatureMeasurement,
        (("when", "date"), ("place", "str"), ("value", "float")),
    ),
}


def try_parse(token: str, field_type: str) -> Tuple[bool, Any]:
    """Попытаться распарсить токен как тип field_type. Возвращает (успех, значение)"""
    try:
        value = TYPE_PARSERS[field_type](token)
        return (True, value)
    except (ValueError, KeyError):
        return (False, None)


def build_object_from_line(line: str) -> Any:
    tokens = tokenize(line.strip())
    if not tokens:
        raise ValueError("Empty input")

    obj_type = tokens[0].lower()
    props = tokens[1:]

    if obj_type not in OBJECT_SCHEMAS:
        raise ValueError(f"Unknown type: {tokens[0]}")

    cls, schema = OBJECT_SCHEMAS[obj_type]
    if len(props) != len(schema):
        raise ValueError("Wrong number of properties")

    # Попытаемся заполнить каждое поле, ища подходящий токен
    kwargs: Dict[str, Any] = {}
    used_indices: set[int] = set()
    
    for field_name, field_type in schema:
        found = False
        
        # Сначала ищем токен в позиции, где он должен быть
        expected_idx = len(used_indices)
        for idx in range(expected_idx, len(props)):
            if idx not in used_indices:
                success, value = try_parse(props[idx], field_type)
                if success:
                    kwargs[field_name] = value
                    used_indices.add(idx)
                    found = True
                    break
        
        # Если не нашли, ищем среди всех оставшихся токенов
        if not found:
            for idx, token in enumerate(props):
                if idx not in used_indices:
                    success, value = try_parse(token, field_type)
                    if success:
                        kwargs[field_name] = value
                        used_indices.add(idx)
                        found = True
                        break
        
        if not found:
            raise ValueError(f"Cannot parse {field_type} from any token: {props}")

    return cls(**kwargs)


def read_objects_from_file(path: str) -> List[Any]:
    objects: List[Any] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                objects.append(build_object_from_line(line))
            except ValueError as e:
                print(f"❌ Ошибка в строке {line_num}: {e}", file=sys.stderr)
                print(f"   Содержимое: {line}", file=sys.stderr)
    return objects


def print_menu() -> None:
    print("\n" + "="*70)
    print("🌡️  ПРОДВИНУТЫЙ МЕТЕОМОНИТОР".center(70))
    print("="*70)
    print("1. 📊 Просмотреть все данные")
    print("2. ➕ Добавить новое измерение")
    print("3. 💾 Сохранить данные в файл")
    print("4. 📂 Загрузить данные из файла")
    print("5. 🔍 Поиск по дате")
    print("6. 📈 Статистика")
    print("7. ❌ Выход")
    print("="*70)


def view_data(objects: List[Any]) -> None:
    if not objects:
        print("\n❌ Нет данных для отображения!")
        return
    
    print("\n" + "="*70)
    print("📊 ИЗМЕРЕНИЯ ТЕМПЕРАТУРЫ".center(70))
    print("="*70 + "\n")
    
    for i, obj in enumerate(objects, 1):
        print(f"  {i}. Дата:        {obj.when.strftime('%d.%m.%Y')}")
        print(f"     Место:       {obj.place}")
        print(f"     Температура: {obj.value:+.1f}°C")
        print()
    
    print("="*70)
    print(f"Всего измерений: {len(objects)}")
    print("="*70)


def add_measurement(objects: List[Any]) -> None:
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


def save_data(objects: List[Any], filepath: str) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for obj in objects:
                date_str = obj.when.strftime("%Y.%m.%d")
                temp_str = f"{obj.value:.1f}".replace(".", ",")
                f.write(f'temperature {date_str} "{obj.place}" {temp_str}\n')
        print(f"✓ Данные сохранены в {filepath}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")


def interactive_mode(input_file: str) -> None:
    objects = read_objects_from_file(input_file)
    
    while True:
        print_menu()
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "1":
            view_data(objects)
        elif choice == "2":
            add_measurement(objects)
        elif choice == "3":
            save_file = input("Введите имя файла для сохранения: ").strip()
            if save_file:
                save_data(objects, save_file)
        elif choice == "4":
            load_file = input("Введите имя файла для загрузки: ").strip()
            if load_file:
                try:
                    new_objects = read_objects_from_file(load_file)
                    objects = new_objects
                    print(f"✓ Данные загружены из {load_file}")
                except Exception as e:
                    print(f"❌ Ошибка при загрузке: {e}")
        elif choice == "5":
            print("До свидания!")
            break
        else:
            print("❌ Неверный выбор!")


def main() -> None:
    # Main entry point for the application
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python program.py <input_file>")
    
    try:
        interactive_mode(sys.argv[1])
    except KeyboardInterrupt:
        print("\n\n⚠️  Приложение прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
