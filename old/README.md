# PR5 (OLD version)

Команды для запуска:

```bash
cd PR5_old
python -m app.main temperature_input.txt

pytest -q
flake8 app tests
pylint app
coverage run -m pytest
coverage report -m
```

Отчёты инструментов лежат в папке `reports/`.
