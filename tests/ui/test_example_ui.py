"""
UI тесты с использованием Selenium - пример для тестирования веб-интерфейсов
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class TestGoogleSearch:
    """Тесты поиска Google"""
    
    @pytest.mark.ui
    @pytest.mark.smoke
    def test_google_search_basic(self, browser):
        """Базовый тест поиска в Google"""
        # Открываем Google
        browser.get("https://www.google.com")
        
        # Находим поле поиска
        search_box = browser.find_element(By.NAME, "q")
        
        # Вводим поисковый запрос
        search_query = "pytest selenium"
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        
        # Ждем загрузки результатов
        wait = WebDriverWait(browser, 10)
        results = wait.until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        # Проверяем, что результаты содержат искомый текст
        assert "pytest" in browser.page_source.lower()
        assert "selenium" in browser.page_source.lower()
    
    def test_google_search_suggestions(self, browser):
        """Тест автодополнения в поиске Google"""
        browser.get("https://www.google.com")
        
        search_box = browser.find_element(By.NAME, "q")
        search_box.send_keys("python")
        
        # Ждем появления подсказок
        time.sleep(1)  # Небольшая задержка для появления подсказок
        
        suggestions = browser.find_elements(By.CSS_SELECTOR, "[role='option']")
        assert len(suggestions) > 0, "Подсказки поиска не появились"
    
    @pytest.mark.parametrize("search_term", [
        "selenium webdriver",
        "pytest tutorial",
        "python automation"
    ])
    def test_google_search_multiple_terms(self, browser, search_term):
        """Параметризованный тест поиска разных терминов"""
        browser.get("https://www.google.com")
        
        search_box = browser.find_element(By.NAME, "q")
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)
        
        # Ждем результатов
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        # Проверяем заголовок страницы
        assert search_term.split()[0] in browser.title.lower()


class TestTodoMVC:
    """Тесты для TodoMVC приложения (пример SPA тестирования)"""
    
    BASE_URL = "https://todomvc.com/examples/react/dist/"
    
    @pytest.mark.ui
    def test_add_todo_item(self, browser):
        """Тест добавления задачи в todo список"""
        browser.get(self.BASE_URL)
        
        # Находим поле ввода
        todo_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "new-todo"))
        )
        
        # Добавляем задачу
        todo_text = "Изучить Selenium"
        todo_input.send_keys(todo_text)
        todo_input.send_keys(Keys.RETURN)
        
        # Проверяем, что задача добавлена
        todo_items = browser.find_elements(By.CSS_SELECTOR, ".todo-list li")
        assert len(todo_items) == 1
        assert todo_text in todo_items[0].text
    
    def test_complete_todo_item(self, browser):
        """Тест отметки задачи как выполненной"""
        browser.get(self.BASE_URL)
        
        # Добавляем задачу
        todo_input = browser.find_element(By.CLASS_NAME, "new-todo")
        todo_input.send_keys("Задача для выполнения")
        todo_input.send_keys(Keys.RETURN)
        
        # Отмечаем как выполненную
        checkbox = browser.find_element(By.CSS_SELECTOR, ".toggle")
        checkbox.click()
        
        # Проверяем, что задача отмечена как выполненная
        completed_items = browser.find_elements(By.CSS_SELECTOR, ".completed")
        assert len(completed_items) == 1
    
    def test_delete_todo_item(self, browser):
        """Тест удаления задачи"""
        browser.get(self.BASE_URL)
        
        # Добавляем задачу
        todo_input = browser.find_element(By.CLASS_NAME, "new-todo")
        todo_input.send_keys("Задача для удаления")
        todo_input.send_keys(Keys.RETURN)
        
        # Наводим курсор на задачу для появления кнопки удаления
        todo_item = browser.find_element(By.CSS_SELECTOR, ".todo-list li")
        actions = ActionChains(browser)
        actions.move_to_element(todo_item).perform()
        
        # Удаляем задачу
        delete_button = browser.find_element(By.CSS_SELECTOR, ".destroy")
        delete_button.click()
        
        # Проверяем, что задача удалена
        todo_items = browser.find_elements(By.CSS_SELECTOR, ".todo-list li")
        assert len(todo_items) == 0
    
    def test_edit_todo_item(self, browser):
        """Тест редактирования задачи"""
        browser.get(self.BASE_URL)
        
        # Добавляем задачу
        todo_input = browser.find_element(By.CLASS_NAME, "new-todo")
        original_text = "Оригинальный текст"
        todo_input.send_keys(original_text)
        todo_input.send_keys(Keys.RETURN)
        
        # Двойной клик для редактирования
        todo_label = browser.find_element(By.CSS_SELECTOR, ".todo-list li label")
        actions = ActionChains(browser)
        actions.double_click(todo_label).perform()
        
        # Редактируем текст
        edit_input = browser.find_element(By.CSS_SELECTOR, ".todo-list li.editing .edit")
        edit_input.clear()
        new_text = "Обновленный текст"
        edit_input.send_keys(new_text)
        edit_input.send_keys(Keys.RETURN)
        
        # Проверяем обновленный текст
        todo_items = browser.find_elements(By.CSS_SELECTOR, ".todo-list li")
        assert new_text in todo_items[0].text
    
    def test_filter_todos(self, browser):
        """Тест фильтрации задач"""
        browser.get(self.BASE_URL)
        
        # Добавляем несколько задач
        todo_input = browser.find_element(By.CLASS_NAME, "new-todo")
        
        # Активная задача
        todo_input.send_keys("Активная задача")
        todo_input.send_keys(Keys.RETURN)
        
        # Выполненная задача
        todo_input.send_keys("Выполненная задача")
        todo_input.send_keys(Keys.RETURN)
        checkboxes = browser.find_elements(By.CSS_SELECTOR, ".toggle")
        checkboxes[1].click()  # Отмечаем вторую как выполненную
        
        # Проверяем фильтр "Active"
        active_filter = browser.find_element(By.LINK_TEXT, "Active")
        active_filter.click()
        visible_todos = browser.find_elements(By.CSS_SELECTOR, ".todo-list li:not([style*='display: none'])")
        assert len(visible_todos) == 1
        
        # Проверяем фильтр "Completed"
        completed_filter = browser.find_element(By.LINK_TEXT, "Completed")
        completed_filter.click()
        visible_todos = browser.find_elements(By.CSS_SELECTOR, ".todo-list li:not([style*='display: none'])")
        assert len(visible_todos) == 1


class TestFormValidation:
    """Тесты валидации форм"""
    
    @pytest.mark.ui
    def test_form_validation_on_practice_site(self, browser):
        """Тест валидации формы на тестовом сайте"""
        browser.get("https://www.selenium.dev/selenium/web/web-form.html")
        
        # Заполняем форму
        text_input = browser.find_element(By.ID, "my-text-id")
        text_input.send_keys("Test text")
        
        password_input = browser.find_element(By.NAME, "my-password")
        password_input.send_keys("SecurePassword123")
        
        textarea = browser.find_element(By.NAME, "my-textarea")
        textarea.send_keys("This is a test message in textarea")
        
        # Выбираем dropdown
        from selenium.webdriver.support.select import Select
        dropdown = Select(browser.find_element(By.NAME, "my-select"))
        dropdown.select_by_visible_text("Two")
        
        # Отправляем форму
        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Проверяем успешную отправку
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        success_message = browser.find_element(By.CLASS_NAME, "alert-success")
        assert "received" in success_message.text.lower()


class TestPageObject:
    """Пример использования Page Object Pattern"""
    
    class GoogleSearchPage:
        """Page Object для страницы поиска Google"""
        
        def __init__(self, driver):
            self.driver = driver
            self.search_box_locator = (By.NAME, "q")
            self.search_button_locator = (By.NAME, "btnK")
            self.results_locator = (By.ID, "search")
        
        def open(self):
            self.driver.get("https://www.google.com")
            return self
        
        def enter_search_term(self, term):
            search_box = self.driver.find_element(*self.search_box_locator)
            search_box.clear()
            search_box.send_keys(term)
            return self
        
        def submit_search(self):
            search_box = self.driver.find_element(*self.search_box_locator)
            search_box.send_keys(Keys.RETURN)
            return self
        
        def wait_for_results(self):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.results_locator)
            )
            return self
        
        def get_results_count(self):
            results = self.driver.find_elements(By.CSS_SELECTOR, "h3")
            return len(results)
    
    @pytest.mark.ui
    def test_search_with_page_object(self, browser):
        """Тест с использованием Page Object"""
        search_page = self.GoogleSearchPage(browser)
        
        results_count = (search_page
                        .open()
                        .enter_search_term("Page Object Pattern")
                        .submit_search()
                        .wait_for_results()
                        .get_results_count())
        
        assert results_count > 0, "Результаты поиска не найдены"


class TestScreenshots:
    """Тесты с созданием скриншотов"""
    
    @pytest.mark.ui
    def test_take_screenshot_on_failure(self, browser, page):
        """Тест создания скриншота при ошибке"""
        try:
            browser.get("https://www.google.com")
            
            # Намеренно вызываем ошибку
            non_existent_element = browser.find_element(By.ID, "non-existent-id")
            
        except NoSuchElementException:
            # Делаем скриншот при ошибке
            screenshot_path = page.screenshot("test_failure")
            assert screenshot_path  # Проверяем, что скриншот создан
            raise  # Пробрасываем исключение дальше


class TestWaitStrategies:
    """Тесты с различными стратегиями ожидания"""
    
    @pytest.mark.ui
    def test_explicit_wait(self, browser):
        """Тест с явным ожиданием"""
        browser.get("https://www.selenium.dev/selenium/web/dynamic.html")
        
        # Нажимаем кнопку, которая добавляет элемент с задержкой
        add_button = browser.find_element(By.ID, "adder")
        add_button.click()
        
        # Явное ожидание появления элемента
        wait = WebDriverWait(browser, 10)
        new_element = wait.until(
            EC.presence_of_element_located((By.ID, "box0"))
        )
        
        assert new_element.is_displayed()
    
    def test_fluent_wait(self, browser):
        """Тест с настраиваемым ожиданием"""
        from selenium.webdriver.support.wait import WebDriverWait
        
        browser.get("https://www.google.com")
        
        # Настраиваемое ожидание с игнорированием исключений
        wait = WebDriverWait(
            browser, 
            timeout=10, 
            poll_frequency=0.5,
            ignored_exceptions=[NoSuchElementException]
        )
        
        search_box = wait.until(
            EC.element_to_be_clickable((By.NAME, "q"))
        )
        
        assert search_box.is_enabled()