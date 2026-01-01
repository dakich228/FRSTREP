"""Program entry point (old)."""

from __future__ import annotations

import sys

from app.ui import interactive_mode


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m app.main <input_file>")

    print("🚀 Запуск приложения Weather Parser v2.0...")
    interactive_mode(sys.argv[1])


if __name__ == "__main__":
    main()
