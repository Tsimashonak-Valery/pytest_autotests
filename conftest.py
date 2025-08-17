"""
Главный файл с фикстурами для всех тестов
"""
import pytest
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Generator, Dict, Any
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from loguru import logger

# Настройка логирования
logger.add(
    "reports/test_run_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Пути к директориям
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# Создание директорий если их нет
for directory in [CONFIG_DIR, DATA_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)


# ========================= Базовые фикстуры =========================

@pytest.fixture(scope="session")
def faker_instance():
    """Фикстура для генерации тестовых данных"""
    return Faker("ru_RU")


@pytest.fixture(scope="session")
def config():
    """Загрузка конфигурации из файла"""
    config_file = CONFIG_DIR / "config.yaml"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "base_url": "https://jsonplaceholder.typicode.com",
        "timeout": 30,
        "browser": "chrome",
        "headless": False
    }


@pytest.fixture
def test_data():
    """Загрузка тестовых данных"""
    data_file = DATA_DIR / "test_data.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ========================= API фикстуры =========================

@pytest.fixture(scope="session")
def api_client(config):
    """HTTP клиент для API тестов"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    # Базовый URL из конфига
    session.base_url = config.get("base_url", "https://jsonplaceholder.typicode.com")
    
    yield session
    session.close()


@pytest.fixture
def api_request(api_client):
    """Обертка для API запросов с логированием"""
    def make_request(method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{api_client.base_url}{endpoint}"
        logger.info(f"API Request: {method} {url}")
        
        response = api_client.request(method, url, **kwargs)
        
        logger.info(f"API Response: {response.status_code}")
        logger.debug(f"Response body: {response.text[:500]}")
        
        return response
    
    return make_request


# ========================= UI фикстуры (Selenium) =========================

@pytest.fixture(scope="function")
def browser(config, request):
    """Фикстура для браузера"""
    logger.info("Starting browser...")
    
    # Настройки Chrome
    chrome_options = Options()
    
    if config.get("headless", False):
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Инициализация драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(config.get("timeout", 10))
    
    # Добавляем драйвер в request для доступа в тестах
    request.cls.driver = driver if hasattr(request, "cls") else None
    
    yield driver
    
    # Закрытие браузера
    logger.info("Closing browser...")
    driver.quit()


@pytest.fixture
def page(browser):
    """Фикстура для работы со страницей"""
    class Page:
        def __init__(self, driver):
            self.driver = driver
        
        def open(self, url: str):
            logger.info(f"Opening URL: {url}")
            self.driver.get(url)
            return self
        
        def screenshot(self, name: str):
            path = REPORTS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(str(path))
            logger.info(f"Screenshot saved: {path}")
            return str(path)
    
    return Page(browser)


# ========================= Фикстуры для работы с данными =========================

@pytest.fixture
def sample_user(faker_instance):
    """Генерация тестового пользователя"""
    return {
        "name": faker_instance.name(),
        "email": faker_instance.email(),
        "username": faker_instance.user_name(),
        "password": faker_instance.password(),
        "phone": faker_instance.phone_number(),
        "address": {
            "street": faker_instance.street_address(),
            "city": faker_instance.city(),
            "zipcode": faker_instance.postcode()
        }
    }


@pytest.fixture
def sample_product(faker_instance):
    """Генерация тестового продукта"""
    return {
        "title": faker_instance.catch_phrase(),
        "description": faker_instance.text(max_nb_chars=200),
        "price": faker_instance.random_number(digits=4),
        "category": faker_instance.random_element(["electronics", "clothing", "books", "food"]),
        "stock": faker_instance.random_int(min=0, max=100)
    }


# ========================= Хуки pytest =========================

def pytest_configure(config):
    """Настройка pytest при запуске"""
    logger.info("Starting test session")
    logger.info(f"Test paths: {config.getoption('testpaths')}")


def pytest_collection_modifyitems(config, items):
    """Модификация собранных тестов"""
    for item in items:
        # Добавляем маркеры на основе пути к файлу
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для создания отчетов о тестах"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        if report.failed:
            logger.error(f"Test failed: {item.nodeid}")
        elif report.passed:
            logger.success(f"Test passed: {item.nodeid}")


# ========================= Параметризованные фикстуры =========================

@pytest.fixture(params=["chrome", "firefox", "edge"])
def browser_name(request):
    """Фикстура для параметризованных тестов с разными браузерами"""
    return request.param


@pytest.fixture(params=[
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 375, "height": 667}  # Mobile
])
def screen_resolution(request):
    """Фикстура для тестирования разных разрешений экрана"""
    return request.param