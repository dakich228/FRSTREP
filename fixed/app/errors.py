"""Custom errors used by the application."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LineError:
    """Represents an error while parsing a single input line."""

    line_no: int
    message: str
    content: str
