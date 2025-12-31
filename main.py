"""Главной файл приложения"""
from __future__ import annotations

import sys

from ui import interactive_mode


def main() -> None:
    """Главная функция приложения"""
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python main.py <input_file>")

    print("🚀 Запуск приложения Weather Parser v2.0...")
    try:
        interactive_mode(sys.argv[1])
    except KeyboardInterrupt:
        print("\n\n⚠️  Приложение прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
    finally:
        print("✓ Приложение завершено")


if __name__ == "__main__":
    main()
