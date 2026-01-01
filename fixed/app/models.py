"""Domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class TemperatureMeasurement:
    """Immutable temperature measurement.

    Attributes:
        when: Measurement date.
        place: Location of measurement.
        value: Temperature value in Celsius.
    """

    when: date
    place: str
    value: float

    def __str__(self) -> str:
        date_s = self.when.strftime("%d.%m.%Y")
        return f"{date_s} | {self.place:20} | {self.value:+.1f}°C"
