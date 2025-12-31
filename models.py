"""Модель данных для хранения информации о температуре"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TemperatureMeasurement:
    """Неизменяемый класс для хранения измерения температуры"""
    when: date
    place: str
    value: float

    def __str__(self) -> str:
        return f"{self.when.strftime('%d.%m.%Y')} | {self.place:20} | {self.value:+.1f}°C"
