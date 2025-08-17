"""
Тесты для проверки работы сервиса ip.me
Сервис возвращает информацию об IP адресе клиента
"""
import pytest
import requests
import re
from assertpy import assert_that


class TestIPMeService:
    """Тесты для сервиса ip.me"""
    
    BASE_URL = "https://ip.me"
    # ip.me не имеет JSON API, поэтому используем альтернативу
    JSON_API_URL = "https://api.ipify.org"
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_ip_address_text(self):
        """Тест получения IP адреса в текстовом формате"""
        # Отправляем запрос
        response = requests.get(self.BASE_URL, headers={"Accept": "text/plain"})
        
        # Проверяем статус код
        assert_that(response.status_code).is_equal_to(200)
        
        # Проверяем, что вернулся IP адрес
        ip_text = response.text.strip()
        
        # IP адрес должен соответствовать формату IPv4 или IPv6
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'
        
        is_valid_ip = (
            re.match(ipv4_pattern, ip_text) is not None or
            re.match(ipv6_pattern, ip_text) is not None
        )
        
        assert_that(is_valid_ip).is_true()
        print(f"Получен IP адрес: {ip_text}")
    
    @pytest.mark.api
    def test_get_ip_info_json(self):
        """Тест получения IP адреса в JSON формате через ipify API"""
        # Используем ipify API для получения JSON
        response = requests.get(f"{self.JSON_API_URL}?format=json")
        
        # Проверяем статус код
        assert_that(response.status_code).is_equal_to(200)
        
        # Проверяем, что вернулся валидный JSON
        data = response.json()
        
        # Проверяем обязательные поля
        assert_that(data).contains_key("ip")
        
        # Проверяем формат IP адреса
        ip_address = data.get("ip")
        assert_that(ip_address).is_not_none()
        
        # Проверяем, что IP адрес не пустой
        assert_that(ip_address).is_not_empty()
        
        print(f"IP адрес из JSON API: {ip_address}")
    
    def test_response_headers(self):
        """Тест проверки заголовков ответа"""
        response = requests.get(self.BASE_URL)
        
        # Проверяем наличие важных заголовков
        assert_that(response.headers).contains_key("Content-Type")
        assert_that(response.headers).contains_key("Server")
        
        # Проверяем, что сервер отвечает быстро
        assert_that(response.elapsed.total_seconds()).is_less_than(5)
    
    @pytest.mark.parametrize("endpoint", [
        "/",
        "/ip",
        "/whois",
    ])
    def test_endpoints_availability(self, endpoint):
        """Параметризованный тест доступности различных endpoints"""
        url = f"https://ip.me{endpoint}"
        response = requests.get(url, timeout=10)
        
        # Все endpoints должны возвращать успешный код
        assert_that(response.status_code).is_equal_to(200)
    
    def test_user_agent_detection(self):
        """Тест с кастомным User-Agent"""
        # Отправляем запрос с кастомным User-Agent
        custom_user_agent = "PyTest/1.0 AutomationTest"
        headers = {"User-Agent": custom_user_agent}
        
        response = requests.get(self.BASE_URL, headers=headers)
        
        assert_that(response.status_code).is_equal_to(200)
        
        # Просто проверяем, что сайт отвечает с кастомным User-Agent
        assert_that(response.text).is_not_empty()
    
    @pytest.mark.slow
    def test_multiple_requests_consistency(self):
        """Тест консистентности при множественных запросах"""
        # Делаем несколько запросов и проверяем, что IP одинаковый
        ip_addresses = []
        
        for _ in range(3):
            response = requests.get(self.BASE_URL, headers={"Accept": "text/plain"})
            assert_that(response.status_code).is_equal_to(200)
            ip_addresses.append(response.text.strip())
        
        # Все полученные IP адреса должны быть одинаковыми (нет дубликатов)
        unique_ips = set(ip_addresses)
        assert_that(len(unique_ips)).is_equal_to(1)
        print(f"Все запросы вернули один IP: {list(unique_ips)[0]}")
    
    def test_ipv4_format_validation(self):
        """Тест валидации формата IPv4 адреса"""
        response = requests.get(self.BASE_URL, headers={"Accept": "text/plain"})
        ip_text = response.text.strip()
        
        # Если это IPv4, проверяем каждую часть
        if '.' in ip_text:
            parts = ip_text.split('.')
            assert_that(parts).is_length(4)
            
            for part in parts:
                # Каждая часть должна быть числом от 0 до 255
                assert_that(part.isdigit()).is_true()
                assert_that(int(part)).is_between(0, 255)
    
    def test_response_time_performance(self):
        """Тест производительности - время ответа"""
        import time
        
        start_time = time.time()
        response = requests.get(self.BASE_URL)
        elapsed_time = time.time() - start_time
        
        # Ответ должен прийти менее чем за 3 секунды
        assert_that(elapsed_time).is_less_than(3)
        assert_that(response.status_code).is_equal_to(200)
        
        print(f"Время ответа: {elapsed_time:.2f} секунд")
    
    @pytest.mark.api
    def test_api_response_structure(self):
        """Тест структуры ответа JSON API"""
        response = requests.get(f"{self.JSON_API_URL}?format=json")
        assert_that(response.status_code).is_equal_to(200)
        
        data = response.json()
        
        # Проверяем типы данных в ответе
        assert_that(data).contains_key("ip")
        assert_that(data["ip"]).is_instance_of(str)
        
        # Проверяем, что IP не локальный
        ip = data.get("ip", "")
        assert_that(ip.startswith("127.")).is_false()
        assert_that(ip.startswith("192.168.")).is_false()
        assert_that(ip.startswith("10.")).is_false()
    
    def test_http_vs_https(self):
        """Тест редиректа с HTTP на HTTPS"""
        # Пробуем HTTP версию (если поддерживается)
        http_url = "http://ip.me"
        
        try:
            response = requests.get(http_url, allow_redirects=False, timeout=5)
            
            # Если есть редирект на HTTPS
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get("Location", "")
                assert_that(location).starts_with("https://")
        except requests.exceptions.RequestException:
            # Если HTTP не поддерживается, это нормально
            pass


class TestIPMeEdgeCases:
    """Тесты граничных случаев для ip.me"""
    
    def test_invalid_endpoint(self):
        """Тест обращения к несуществующему endpoint"""
        response = requests.get("https://ip.me/nonexistent")
        
        # ip.me возвращает 200 для всех запросов (возвращает IP или главную страницу)
        assert_that(response.status_code).is_equal_to(200)
    
    def test_options_request(self):
        """Тест OPTIONS запроса для проверки CORS"""
        response = requests.options("https://ip.me/api")
        
        # ip.me возвращает 200 для OPTIONS запросов
        assert_that(response.status_code).is_equal_to(200)
    
    def test_head_request(self):
        """Тест HEAD запроса"""
        response = requests.head("https://ip.me")
        
        # HEAD должен вернуть успешный статус без тела
        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.text).is_empty()
    
    @pytest.mark.skip(reason="Может вызвать rate limiting")
    def test_rate_limiting(self):
        """Тест на rate limiting (пропускаем по умолчанию)"""
        # Делаем много запросов подряд
        responses = []
        for _ in range(20):
            response = requests.get("https://ip.me/api")
            responses.append(response.status_code)
        
        # Проверяем, не заблокировали ли нас
        blocked_codes = [429, 503]  # Too Many Requests или Service Unavailable
        assert_that(responses).does_not_contain(*blocked_codes)