"""Парсинг различных типов данных"""
from __future__ import annotations

import re
from datetime import date, datetime, time
from typing import Any, Tuple


RE_DATE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
RE_TIME = re.compile(r"^\d{2}:\d{2}$")
RE_INT = re.compile(r"^[+-]?\d+$")
RE_FLOAT = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


def parse_date_yyyymmdd(token: str) -> date:
    """Парсить дату в формате YYYY.MM.DD"""
    if not RE_DATE.match(token):
        raise ValueError(f"Invalid date: {token}")
    return datetime.strptime(token, "%Y.%m.%d").date()


def parse_time_hhmm(token: str) -> time:
    """Парсить время в формате HH:MM"""
    if not RE_TIME.match(token):
        raise ValueError(f"Invalid time: {token}")
    return datetime.strptime(token, "%H:%M").time()


def parse_int(token: str) -> int:
    """Парсить целое число"""
    if not RE_INT.match(token):
        raise ValueError(f"Invalid int: {token}")
    return int(token)


def parse_float(token: str) -> float:
    """Парсить число с плавающей точкой (поддерживает точку и запятую)"""
    if not RE_FLOAT.match(token):
        raise ValueError(f"Invalid float: {token}")
    return float(token.replace(",", "."))


def parse_str(token: str) -> str:
    """Парсить строку"""
    return token


def try_parse(token: str, field_type: str) -> Tuple[bool, Any]:
    """Попытаться распарсить токен как тип field_type. Возвращает (успех, значение)"""
    type_parsers = {
        "date": parse_date_yyyymmdd,
        "time": parse_time_hhmm,
        "int": parse_int,
        "float": parse_float,
        "str": parse_str,
    }
    
    try:
        parser = type_parsers.get(field_type)
        if not parser:
            return (False, None)
        value = parser(token)
        return (True, value)
    except (ValueError, KeyError):
        return (False, None)
