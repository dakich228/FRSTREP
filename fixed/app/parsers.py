"""Parsing utilities for supported value types."""

from __future__ import annotations

import re
from datetime import date, datetime, time
from typing import Any, Callable, Dict, Tuple

RE_DATE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
RE_TIME = re.compile(r"^\d{2}:\d{2}$")
RE_INT = re.compile(r"^[+-]?\d+$")
RE_FLOAT = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


def parse_date_yyyymmdd(token: str) -> date:
    """Parse date in YYYY.MM.DD format."""
    if not RE_DATE.match(token):
        raise ValueError(f"Invalid date: {token}")
    return datetime.strptime(token, "%Y.%m.%d").date()


def parse_time_hhmm(token: str) -> time:
    """Parse time in HH:MM format."""
    if not RE_TIME.match(token):
        raise ValueError(f"Invalid time: {token}")
    return datetime.strptime(token, "%H:%M").time()


def parse_int(token: str) -> int:
    """Parse integer."""
    if not RE_INT.match(token):
        raise ValueError(f"Invalid int: {token}")
    return int(token)


def parse_float(token: str) -> float:
    """Parse float; supports ',' or '.' as decimal separator."""
    if not RE_FLOAT.match(token):
        raise ValueError(f"Invalid float: {token}")
    return float(token.replace(",", "."))


def parse_str(token: str) -> str:
    """Return token as-is."""
    return token


TYPE_PARSERS: Dict[str, Callable[[str], Any]] = {
    "date": parse_date_yyyymmdd,
    "time": parse_time_hhmm,
    "int": parse_int,
    "float": parse_float,
    "str": parse_str,
}


def try_parse(token: str, field_type: str) -> Tuple[bool, Any]:
    """Try parsing token into the requested field type."""
    parser = TYPE_PARSERS.get(field_type)
    if parser is None:
        return False, None
    try:
        return True, parser(token)
    except ValueError:
        return False, None
