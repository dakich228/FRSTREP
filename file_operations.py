"""Работа с файлами и токенизация"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence, Tuple

from models import TemperatureMeasurement
from parsers import try_parse


TOKEN_RE = re.compile(r'"([^"]*)"|(\S+)')

FieldSpec = Tuple[str, str]
SchemaSpec = Tuple[type, Sequence[FieldSpec]]

OBJECT_SCHEMAS: Dict[str, SchemaSpec] = {
    "temperature": (
        TemperatureMeasurement,
        (("when", "date"), ("place", "str"), ("value", "float")),
    ),
}


def tokenize(line: str) -> List[str]:
    """Разбить строку на токены"""
    return [q if q else b for q, b in TOKEN_RE.findall(line)]


def build_object_from_line(line: str) -> Any:
    """Построить объект из строки с автоматическим определением типов"""
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

    kwargs: Dict[str, Any] = {}
    used_indices: set[int] = set()
    
    for field_name, field_type in schema:
        found = False
        
        expected_idx = len(used_indices)
        for idx in range(expected_idx, len(props)):
            if idx not in used_indices:
                success, value = try_parse(props[idx], field_type)
                if success:
                    kwargs[field_name] = value
                    used_indices.add(idx)
                    found = True
                    break
        
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
    """Прочитать объекты из файла с обработкой ошибок"""
    objects: List[Any] = []
    errors: List[Tuple[int, str, str]] = []
    
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                objects.append(build_object_from_line(line))
            except ValueError as e:
                errors.append((line_num, str(e), line))
    
    return objects, errors


def save_objects_to_file(objects: List[Any], filepath: str) -> None:
    """Сохранить объекты в файл"""
    with open(filepath, "w", encoding="utf-8") as f:
        for obj in objects:
            date_str = obj.when.strftime("%Y.%m.%d")
            temp_str = f"{obj.value:.1f}".replace(".", ",")
            f.write(f'temperature {date_str} "{obj.place}" {temp_str}\n')
