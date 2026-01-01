"""Tokenization and file I/O."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence, Tuple

from app.errors import LineError
from app.models import TemperatureMeasurement
from app.parsers import try_parse

TOKEN_RE = re.compile(r'"([^"]*)"|(\S+)')

FieldSpec = Tuple[str, str]
SchemaSpec = Tuple[type, Sequence[FieldSpec]]

OBJECT_SCHEMAS: Dict[str, SchemaSpec] = {
    "temperature": (
        TemperatureMeasurement,
        (("when", "date"), ("place", "str"), ("value", "float")),
    )
}


def tokenize(line: str) -> List[str]:
    """Split a line into tokens.

    Tokens may be quoted using double quotes.
    """
    return [q if q else b for q, b in TOKEN_RE.findall(line)]


def _pick_value(
    props: List[str],
    used: set[int],
    ftype: str,
    start: int,
) -> Tuple[bool, Any, int]:
    """Pick a token that matches the requested type.

    The function prefers the original order of tokens: it first searches
    from `start` to the end, and only then scans from the beginning.
    """
    for idx in range(start, len(props)):
        if idx in used:
            continue
        ok, value = try_parse(props[idx], ftype)
        if ok:
            return True, value, idx

    for idx, token in enumerate(props):
        if idx in used:
            continue
        ok, value = try_parse(token, ftype)
        if ok:
            return True, value, idx

    return False, None, -1


def build_object_from_line(line: str) -> Any:
    """Build a domain object from a single input line."""
    tokens = tokenize(line.strip())
    if not tokens:
        raise ValueError("Empty input")

    obj_type = tokens[0].lower()
    schema = OBJECT_SCHEMAS.get(obj_type)
    if schema is None:
        raise ValueError(f"Unknown type: {tokens[0]}")

    cls, fields = schema
    props = tokens[1:]
    if len(props) != len(fields):
        raise ValueError("Wrong number of properties")

    kwargs: Dict[str, Any] = {}
    used: set[int] = set()

    for name, ftype in fields:
        start = len(used)
        ok, value, idx = _pick_value(props, used, ftype, start)
        if not ok:
            raise ValueError(f"Cannot parse {ftype} from tokens: {props}")
        kwargs[name] = value
        used.add(idx)

    return cls(**kwargs)


def read_objects_from_file(path: str) -> Tuple[List[Any], List[LineError]]:
    """Read objects from a text file.

    Returns a tuple: (objects, errors).
    """
    objects: List[Any] = []
    errors: List[LineError] = []

    with open(path, "r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                objects.append(build_object_from_line(line))
            except ValueError as exc:
                errors.append(LineError(line_no, str(exc), line))

    return objects, errors


def save_objects_to_file(objects: List[Any], filepath: str) -> None:
    """Save objects to a text file in the same input format."""
    with open(filepath, "w", encoding="utf-8") as handle:
        for obj in objects:
            date_str = obj.when.strftime("%Y.%m.%d")
            temp_str = f"{obj.value:.1f}".replace(".", ",")
            handle.write(
                f'temperature {date_str} "{obj.place}" {temp_str}\n'
            )
