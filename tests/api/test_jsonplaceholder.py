"""
API тесты для JSONPlaceholder - бесплатного REST API для тестирования
https://jsonplaceholder.typicode.com/
"""
import pytest
import requests
from jsonschema import validate
from assertpy import assert_that


class TestJSONPlaceholderAPI:
    """Тесты для JSONPlaceholder API"""
    
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    # ============== Схемы для валидации ==============
    
    USER_SCHEMA = {
        "type": "object",
        "required": ["id", "name", "username", "email"],
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "username": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "address": {"type": "object"},
            "phone": {"type": "string"},
            "website": {"type": "string"},
            "company": {"type": "object"}
        }
    }
    
    POST_SCHEMA = {
        "type": "object",
        "required": ["userId", "id", "title", "body"],
        "properties": {
            "userId": {"type": "integer"},
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "body": {"type": "string"}
        }
    }
    
    # ============== Тесты GET запросов ==============
    
    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_all_users(self):
        """Тест получения списка всех пользователей"""
        response = requests.get(f"{self.BASE_URL}/users")
        
        assert_that(response.status_code).is_equal_to(200)
        users = response.json()
        
        assert_that(users).is_not_empty()
        assert_that(users).is_instance_of(list)
        assert_that(len(users)).is_equal_to(10)
        
        # Валидация первого пользователя по схеме
        validate(instance=users[0], schema=self.USER_SCHEMA)
    
    def test_get_user_by_id(self):
        """Тест получения пользователя по ID"""
        user_id = 1
        response = requests.get(f"{self.BASE_URL}/users/{user_id}")
        
        assert_that(response.status_code).is_equal_to(200)
        user = response.json()
        
        assert_that(user["id"]).is_equal_to(user_id)
        assert_that(user["name"]).is_equal_to("Leanne Graham")
        assert_that(user["email"]).contains("@")
        
        # Валидация по схеме
        validate(instance=user, schema=self.USER_SCHEMA)
    
    def test_get_nonexistent_user(self):
        """Тест получения несуществующего пользователя"""
        response = requests.get(f"{self.BASE_URL}/users/999")
        
        assert_that(response.status_code).is_equal_to(404)
        assert_that(response.json()).is_equal_to({})
    
    @pytest.mark.parametrize("post_id", [1, 2, 5, 10])
    def test_get_post_by_id(self, post_id):
        """Параметризованный тест получения постов по ID"""
        response = requests.get(f"{self.BASE_URL}/posts/{post_id}")
        
        assert_that(response.status_code).is_equal_to(200)
        post = response.json()
        
        assert_that(post["id"]).is_equal_to(post_id)
        validate(instance=post, schema=self.POST_SCHEMA)
    
    def test_get_posts_by_user(self):
        """Тест получения постов конкретного пользователя"""
        user_id = 1
        response = requests.get(f"{self.BASE_URL}/posts", params={"userId": user_id})
        
        assert_that(response.status_code).is_equal_to(200)
        posts = response.json()
        
        assert_that(posts).is_not_empty()
        for post in posts:
            assert_that(post["userId"]).is_equal_to(user_id)
    
    # ============== Тесты POST запросов ==============
    
    @pytest.mark.smoke
    def test_create_post(self):
        """Тест создания нового поста"""
        new_post = {
            "title": "Test Post",
            "body": "This is a test post body",
            "userId": 1
        }
        
        response = requests.post(f"{self.BASE_URL}/posts", json=new_post)
        
        assert_that(response.status_code).is_equal_to(201)
        created_post = response.json()
        
        assert_that(created_post["title"]).is_equal_to(new_post["title"])
        assert_that(created_post["body"]).is_equal_to(new_post["body"])
        assert_that(created_post["userId"]).is_equal_to(new_post["userId"])
        assert_that(created_post).contains_key("id")
    
    def test_create_post_with_invalid_data(self):
        """Тест создания поста с невалидными данными"""
        invalid_post = {
            "title": "",  # Пустой заголовок
            "body": "",   # Пустое тело
            "userId": "not_a_number"  # Неверный тип userId
        }
        
        response = requests.post(f"{self.BASE_URL}/posts", json=invalid_post)
        
        # JSONPlaceholder все равно создаст пост (это особенность мок-API)
        assert_that(response.status_code).is_equal_to(201)
    
    # ============== Тесты PUT запросов ==============
    
    def test_update_post(self):
        """Тест обновления существующего поста"""
        post_id = 1
        updated_data = {
            "id": post_id,
            "title": "Updated Title",
            "body": "Updated body content",
            "userId": 1
        }
        
        response = requests.put(f"{self.BASE_URL}/posts/{post_id}", json=updated_data)
        
        assert_that(response.status_code).is_equal_to(200)
        updated_post = response.json()
        
        assert_that(updated_post["title"]).is_equal_to(updated_data["title"])
        assert_that(updated_post["body"]).is_equal_to(updated_data["body"])
    
    # ============== Тесты PATCH запросов ==============
    
    def test_partial_update_post(self):
        """Тест частичного обновления поста"""
        post_id = 1
        patch_data = {
            "title": "Only Title Updated"
        }
        
        response = requests.patch(f"{self.BASE_URL}/posts/{post_id}", json=patch_data)
        
        assert_that(response.status_code).is_equal_to(200)
        patched_post = response.json()
        
        assert_that(patched_post["title"]).is_equal_to(patch_data["title"])
        assert_that(patched_post).contains_key("body")  # Остальные поля должны остаться
    
    # ============== Тесты DELETE запросов ==============
    
    def test_delete_post(self):
        """Тест удаления поста"""
        post_id = 1
        response = requests.delete(f"{self.BASE_URL}/posts/{post_id}")
        
        assert_that(response.status_code).is_equal_to(200)
        # После удаления обычно возвращается пустой объект
        assert_that(response.json()).is_equal_to({})
    
    # ============== Тесты с использованием фикстур из conftest ==============
    
    def test_with_api_client_fixture(self, api_request):
        """Тест с использованием фикстуры api_request из conftest.py"""
        response = api_request("GET", "/users/1")
        
        assert_that(response.status_code).is_equal_to(200)
        user = response.json()
        assert_that(user["id"]).is_equal_to(1)
    
    # ============== Тесты производительности ==============
    
    @pytest.mark.slow
    def test_api_response_time(self):
        """Тест времени ответа API"""
        import time
        
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/users")
        elapsed_time = time.time() - start_time
        
        assert_that(response.status_code).is_equal_to(200)
        assert_that(elapsed_time).is_less_than(2)  # Ответ должен прийти менее чем за 2 секунды
    
    # ============== Тесты с комбинацией запросов ==============
    
    def test_user_posts_relationship(self):
        """Тест связи между пользователями и их постами"""
        # Получаем пользователя
        user_response = requests.get(f"{self.BASE_URL}/users/1")
        assert_that(user_response.status_code).is_equal_to(200)
        user = user_response.json()
        
        # Получаем посты этого пользователя
        posts_response = requests.get(f"{self.BASE_URL}/posts", params={"userId": user["id"]})
        assert_that(posts_response.status_code).is_equal_to(200)
        posts = posts_response.json()
        
        # Проверяем, что у пользователя есть посты
        assert_that(posts).is_not_empty()
        
        # Проверяем, что все посты принадлежат этому пользователю
        for post in posts:
            assert_that(post["userId"]).is_equal_to(user["id"])


class TestJSONPlaceholderComments:
    """Тесты для работы с комментариями"""
    
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    def test_get_comments_for_post(self):
        """Тест получения комментариев к посту"""
        post_id = 1
        response = requests.get(f"{self.BASE_URL}/posts/{post_id}/comments")
        
        assert_that(response.status_code).is_equal_to(200)
        comments = response.json()
        
        assert_that(comments).is_not_empty()
        for comment in comments:
            assert_that(comment["postId"]).is_equal_to(post_id)
            assert_that(comment["email"]).contains("@")
    
    def test_filter_comments_by_email(self):
        """Тест фильтрации комментариев по email"""
        email = "Eliseo@gardner.biz"
        response = requests.get(f"{self.BASE_URL}/comments", params={"email": email})
        
        assert_that(response.status_code).is_equal_to(200)
        comments = response.json()
        
        for comment in comments:
            assert_that(comment["email"]).is_equal_to(email)


class TestJSONPlaceholderAlbums:
    """Тесты для работы с альбомами и фотографиями"""
    
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    @pytest.mark.integration
    def test_user_albums_photos_chain(self):
        """Интеграционный тест: пользователь -> альбомы -> фотографии"""
        user_id = 1
        
        # Получаем альбомы пользователя
        albums_response = requests.get(f"{self.BASE_URL}/albums", params={"userId": user_id})
        assert_that(albums_response.status_code).is_equal_to(200)
        albums = albums_response.json()
        assert_that(albums).is_not_empty()
        
        # Для первого альбома получаем фотографии
        first_album = albums[0]
        photos_response = requests.get(
            f"{self.BASE_URL}/photos", 
            params={"albumId": first_album["id"]}
        )
        assert_that(photos_response.status_code).is_equal_to(200)
        photos = photos_response.json()
        
        # Проверяем фотографии
        assert_that(photos).is_not_empty()
        for photo in photos:
            assert_that(photo["albumId"]).is_equal_to(first_album["id"])
            assert_that(photo["url"]).starts_with("https://")
            assert_that(photo["thumbnailUrl"]).starts_with("https://")