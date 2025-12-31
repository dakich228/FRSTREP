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


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python program.py <input_file>")

    objects = read_objects_from_file(sys.argv[1])
    
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


if __name__ == "__main__":
    main()
