"""
Интеграционные тесты для проверки обработки данных
"""
import pytest
import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from faker import Faker


class DataProcessor:
    """Класс для обработки данных - пример для интеграционных тестов"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
    
    def save_to_json(self, data: Dict[str, Any], filename: str) -> Path:
        """Сохранение данных в JSON файл"""
        file_path = self.data_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path
    
    def load_from_json(self, filename: str) -> Dict[str, Any]:
        """Загрузка данных из JSON файла"""
        file_path = self.data_dir / filename
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_to_csv(self, data: List[Dict], filename: str) -> Path:
        """Сохранение данных в CSV файл"""
        file_path = self.data_dir / filename
        if data:
            keys = data[0].keys()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        return file_path
    
    def load_from_csv(self, filename: str) -> List[Dict]:
        """Загрузка данных из CSV файла"""
        file_path = self.data_dir / filename
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def transform_data(self, data: List[Dict]) -> List[Dict]:
        """Трансформация данных - добавление вычисляемых полей"""
        for item in data:
            if "price" in item and "quantity" in item:
                item["total"] = float(item["price"]) * int(item["quantity"])
            if "first_name" in item and "last_name" in item:
                item["full_name"] = f"{item['first_name']} {item['last_name']}"
        return data
    
    def filter_data(self, data: List[Dict], **filters) -> List[Dict]:
        """Фильтрация данных по заданным критериям"""
        result = data
        for key, value in filters.items():
            result = [item for item in result if item.get(key) == value]
        return result


class TestDataProcessorIntegration:
    """Интеграционные тесты для DataProcessor"""
    
    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Временная директория для тестовых данных"""
        return tmp_path / "test_data"
    
    @pytest.fixture
    def processor(self, temp_data_dir):
        """Экземпляр DataProcessor"""
        return DataProcessor(temp_data_dir)
    
    @pytest.fixture
    def sample_products(self, faker_instance):
        """Тестовые данные - продукты"""
        products = []
        for i in range(10):
            products.append({
                "id": i + 1,
                "name": faker_instance.catch_phrase(),
                "price": faker_instance.random_number(digits=3),
                "quantity": faker_instance.random_int(min=1, max=100),
                "category": faker_instance.random_element(["electronics", "clothing", "food"])
            })
        return products
    
    @pytest.fixture
    def sample_users(self, faker_instance):
        """Тестовые данные - пользователи"""
        users = []
        for i in range(5):
            users.append({
                "id": i + 1,
                "first_name": faker_instance.first_name(),
                "last_name": faker_instance.last_name(),
                "email": faker_instance.email(),
                "city": faker_instance.city()
            })
        return users
    
    # ============== Тесты сохранения и загрузки ==============
    
    @pytest.mark.integration
    def test_save_and_load_json(self, processor, sample_products):
        """Тест сохранения и загрузки JSON"""
        # Сохраняем данные
        file_path = processor.save_to_json(
            {"products": sample_products}, 
            "products.json"
        )
        
        assert file_path.exists()
        
        # Загружаем данные
        loaded_data = processor.load_from_json("products.json")
        
        assert "products" in loaded_data
        assert len(loaded_data["products"]) == len(sample_products)
        assert loaded_data["products"] == sample_products
    
    def test_save_and_load_csv(self, processor, sample_users):
        """Тест сохранения и загрузки CSV"""
        # Сохраняем данные
        file_path = processor.save_to_csv(sample_users, "users.csv")
        
        assert file_path.exists()
        
        # Загружаем данные
        loaded_data = processor.load_from_csv("users.csv")
        
        assert len(loaded_data) == len(sample_users)
        
        # Проверяем первую запись
        # Числовые значения в CSV становятся строками
        assert loaded_data[0]["first_name"] == sample_users[0]["first_name"]
        assert loaded_data[0]["email"] == sample_users[0]["email"]
    
    # ============== Тесты трансформации данных ==============
    
    def test_transform_products_adds_total(self, processor, sample_products):
        """Тест добавления поля total к продуктам"""
        transformed = processor.transform_data(sample_products.copy())
        
        for product in transformed:
            assert "total" in product
            expected_total = product["price"] * product["quantity"]
            assert product["total"] == expected_total
    
    def test_transform_users_adds_full_name(self, processor, sample_users):
        """Тест добавления поля full_name к пользователям"""
        transformed = processor.transform_data(sample_users.copy())
        
        for user in transformed:
            assert "full_name" in user
            expected_name = f"{user['first_name']} {user['last_name']}"
            assert user["full_name"] == expected_name
    
    # ============== Тесты фильтрации ==============
    
    def test_filter_by_category(self, processor, sample_products):
        """Тест фильтрации продуктов по категории"""
        electronics = processor.filter_data(
            sample_products, 
            category="electronics"
        )
        
        for product in electronics:
            assert product["category"] == "electronics"
    
    def test_filter_by_multiple_criteria(self, processor, sample_products):
        """Тест фильтрации по нескольким критериям"""
        # Добавляем поле для фильтрации
        sample_products[0]["category"] = "electronics"
        sample_products[0]["quantity"] = 50
        
        filtered = processor.filter_data(
            sample_products,
            category="electronics",
            quantity=50
        )
        
        assert len(filtered) >= 1
        assert all(p["category"] == "electronics" for p in filtered)
        assert all(p["quantity"] == 50 for p in filtered)
    
    # ============== Комплексные интеграционные тесты ==============
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_data_pipeline(self, processor, sample_products):
        """Полный цикл обработки данных"""
        # 1. Трансформируем данные
        transformed = processor.transform_data(sample_products.copy())
        
        # 2. Фильтруем данные
        filtered = processor.filter_data(
            transformed, 
            category=sample_products[0]["category"]
        )
        
        # 3. Сохраняем в JSON
        json_path = processor.save_to_json(
            {"filtered_products": filtered}, 
            "filtered.json"
        )
        
        # 4. Сохраняем в CSV
        csv_path = processor.save_to_csv(filtered, "filtered.csv")
        
        # 5. Загружаем обратно и проверяем
        json_data = processor.load_from_json("filtered.json")
        csv_data = processor.load_from_csv("filtered.csv")
        
        assert json_path.exists()
        assert csv_path.exists()
        assert len(json_data["filtered_products"]) == len(filtered)
        assert len(csv_data) == len(filtered)
    
    def test_empty_data_handling(self, processor):
        """Тест обработки пустых данных"""
        empty_list = []
        
        # Трансформация пустых данных
        transformed = processor.transform_data(empty_list)
        assert transformed == []
        
        # Фильтрация пустых данных
        filtered = processor.filter_data(empty_list, any_field="value")
        assert filtered == []
        
        # Сохранение пустых данных
        csv_path = processor.save_to_csv(empty_list, "empty.csv")
        assert csv_path.exists()
    
    def test_data_consistency_across_formats(self, processor, sample_users):
        """Тест консистентности данных между форматами"""
        # Трансформируем данные
        transformed = processor.transform_data(sample_users.copy())
        
        # Сохраняем в оба формата
        processor.save_to_json({"users": transformed}, "users.json")
        processor.save_to_csv(transformed, "users.csv")
        
        # Загружаем обратно
        json_users = processor.load_from_json("users.json")["users"]
        csv_users = processor.load_from_csv("users.csv")
        
        # Проверяем консистентность
        assert len(json_users) == len(csv_users)
        
        for i, (json_user, csv_user) in enumerate(zip(json_users, csv_users)):
            # CSV возвращает все как строки, поэтому сравниваем только строковые поля
            assert json_user["first_name"] == csv_user["first_name"]
            assert json_user["last_name"] == csv_user["last_name"]
            assert json_user["email"] == csv_user["email"]
            assert json_user["full_name"] == csv_user["full_name"]
    
    @pytest.mark.parametrize("num_records", [10, 100, 1000])
    def test_performance_with_different_data_sizes(self, processor, faker_instance, num_records):
        """Тест производительности с разными объемами данных"""
        import time
        
        # Генерируем данные
        large_dataset = [
            {
                "id": i,
                "name": faker_instance.name(),
                "value": faker_instance.random_number()
            }
            for i in range(num_records)
        ]
        
        # Замеряем время обработки
        start_time = time.time()
        
        processor.save_to_json({"data": large_dataset}, f"large_{num_records}.json")
        loaded = processor.load_from_json(f"large_{num_records}.json")
        
        elapsed_time = time.time() - start_time
        
        # Проверяем корректность и производительность
        assert len(loaded["data"]) == num_records
        assert elapsed_time < 5  # Должно выполниться менее чем за 5 секунд


class TestDataValidation:
    """Тесты валидации данных"""
    
    @pytest.fixture
    def processor(self, tmp_path):
        return DataProcessor(tmp_path / "validation_test")
    
    def test_invalid_json_handling(self, processor, tmp_path):
        """Тест обработки невалидного JSON"""
        # Создаем невалидный JSON файл
        invalid_file = processor.data_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            processor.load_from_json("invalid.json")
    
    def test_missing_file_handling(self, processor):
        """Тест обработки отсутствующего файла"""
        with pytest.raises(FileNotFoundError):
            processor.load_from_json("nonexistent.json")
    
    def test_unicode_data_handling(self, processor):
        """Тест обработки Unicode данных"""
        unicode_data = {
            "русский": "текст",
            "中文": "文字",
            "emoji": "😀🎉",
            "special": "©®™"
        }
        
        # Сохраняем и загружаем
        processor.save_to_json(unicode_data, "unicode.json")
        loaded = processor.load_from_json("unicode.json")
        
        assert loaded == unicode_data