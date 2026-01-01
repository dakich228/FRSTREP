# PR5 (FIXED version)

Команды для запуска:

```bash
cd PR5_fixed
python -m app.main temperature_input.txt

pytest
flake8 app tests
pylint app
coverage run -m pytest
coverage report -m
```

Результаты запусков сохранены в папке `reports/`.
