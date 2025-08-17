# Проект автотестов на Pytest

Учебный проект для практики написания автотестов с использованием pytest.

## Структура проекта

```
pytest_autotests/
├── tests/                  # Директория с тестами
│   ├── unit/              # Unit тесты
│   ├── integration/       # Интеграционные тесты
│   ├── api/               # API тесты
│   └── ui/                # UI тесты (Selenium)
├── src/                   # Исходный код приложения
├── utils/                 # Вспомогательные утилиты
├── config/                # Конфигурационные файлы
├── data/                  # Тестовые данные
├── reports/               # Отчеты о тестировании
├── conftest.py            # Глобальные фикстуры
├── pytest.ini             # Конфигурация pytest
└── requirements.txt       # Зависимости проекта
```

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск тестов

### Все тесты
```bash
pytest
```

### Конкретная категория тестов
```bash
# Unit тесты
pytest tests/unit/

# API тесты
pytest tests/api/

# UI тесты
pytest tests/ui/

# Интеграционные тесты
pytest tests/integration/
```

### Тесты по маркерам
```bash
# Только smoke тесты
pytest -m smoke

# Только API тесты
pytest -m api

# Исключить медленные тесты
pytest -m "not slow"

# Smoke тесты, но не UI
pytest -m "smoke and not ui"
```

### С различными опциями
```bash
# Подробный вывод
pytest -v

# Показать print() выводы
pytest -s

# Остановиться после первой ошибки
pytest -x

# Запустить последние упавшие тесты
pytest --lf

# Параллельный запуск (4 процесса)
pytest -n 4

# С генерацией HTML отчета
pytest --html=reports/report.html --self-contained-html
```

## Примеры тестов

### Unit тест (test_calculator.py)
```python
def test_add_positive_numbers(calc):
    assert calc.add(2, 3) == 5
```

### API тест (test_jsonplaceholder.py)
```python
def test_get_user_by_id():
    response = requests.get(f"{BASE_URL}/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
```

### UI тест (test_example_ui.py)
```python
def test_google_search(browser):
    browser.get("https://www.google.com")
    search_box = browser.find_element(By.NAME, "q")
    search_box.send_keys("pytest")
    search_box.send_keys(Keys.RETURN)
    assert "pytest" in browser.page_source
```

## Фикстуры

Основные фикстуры определены в `conftest.py`:

- `faker_instance` - генератор тестовых данных
- `config` - конфигурация из файла
- `api_client` - HTTP клиент для API тестов
- `browser` - WebDriver для UI тестов
- `sample_user` - тестовый пользователь
- `sample_product` - тестовый продукт

## Маркеры

Доступные маркеры для тестов:

- `@pytest.mark.smoke` - быстрые критичные тесты
- `@pytest.mark.regression` - полный набор тестов
- `@pytest.mark.slow` - медленные тесты
- `@pytest.mark.api` - API тесты
- `@pytest.mark.ui` - UI тесты
- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.integration` - интеграционные тесты
- `@pytest.mark.skip_ci` - пропустить в CI/CD

## Параметризация

Пример параметризованного теста:
```python
@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0)
])
def test_add(calc, a, b, expected):
    assert calc.add(a, b) == expected
```

## Отчеты

### HTML отчет
После запуска тестов HTML отчет будет доступен в `reports/report.html`

### Allure отчет
```bash
# Запуск с Allure
pytest --alluredir=reports/allure

# Просмотр отчета
allure serve reports/allure
```

## Логирование

Логи сохраняются в `reports/pytest.log` и `reports/test_run_*.log`

Уровни логирования:
- Консоль: INFO
- Файл: DEBUG

## Полезные команды

```bash
# Показать все доступные фикстуры
pytest --fixtures

# Показать все маркеры
pytest --markers

# Собрать тесты без запуска
pytest --collect-only

# Профилирование медленных тестов
pytest --durations=10

# Покрытие кода (требует pytest-cov)
pytest --cov=src --cov-report=html
```

## Конфигурация

### pytest.ini
Основные настройки pytest находятся в `pytest.ini`

### Переменные окружения
Создайте файл `.env` для локальных настроек:
```
BASE_URL=https://your-api.com
BROWSER=chrome
HEADLESS=false
```

## Советы по написанию тестов

1. **Используйте говорящие имена** - `test_user_can_login_with_valid_credentials`
2. **Один тест - одна проверка** - не перегружайте тесты множеством assert'ов
3. **Используйте фикстуры** - для переиспользования кода и setup/teardown
4. **Группируйте тесты** - используйте классы для логической группировки
5. **Добавляйте маркеры** - для удобного запуска подмножества тестов
6. **Параметризуйте** - вместо копирования похожих тестов
7. **Документируйте** - добавляйте docstring к сложным тестам

## Troubleshooting

### ChromeDriver не найден
```bash
# Установится автоматически через webdriver-manager
# Или установите вручную:
brew install chromedriver  # macOS
```

### Тесты медленно выполняются
- Используйте параллельный запуск: `pytest -n auto`
- Отключите UI в браузере: установите `headless=true` в конфиге
- Используйте маркер `@pytest.mark.slow` и исключайте при обычных прогонах

### Flaky тесты
- Используйте `pytest-rerunfailures`: `pytest --reruns 3`
- Добавьте явные ожидания в UI тестах
- Проверьте тестовые данные на уникальность