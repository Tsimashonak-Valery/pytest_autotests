"""
Unit тесты для калькулятора - пример для изучения основ pytest
"""
import pytest
from typing import Union


class Calculator:
    """Простой калькулятор для демонстрации unit тестов"""
    
    @staticmethod
    def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        return a + b
    
    @staticmethod
    def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        return a - b
    
    @staticmethod
    def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        return a * b
    
    @staticmethod
    def divide(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b
    
    @staticmethod
    def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        return base ** exponent


class TestCalculator:
    """Тесты для класса Calculator"""
    
    @pytest.fixture
    def calc(self):
        """Фикстура для создания экземпляра калькулятора"""
        return Calculator()
    
    # ============== Тесты сложения ==============
    
    def test_add_positive_numbers(self, calc):
        """Тест сложения положительных чисел"""
        assert calc.add(2, 3) == 5
        assert calc.add(10, 20) == 30
    
    def test_add_negative_numbers(self, calc):
        """Тест сложения отрицательных чисел"""
        assert calc.add(-5, -3) == -8
        assert calc.add(-10, 5) == -5
    
    @pytest.mark.parametrize("a, b, expected", [
        (0, 0, 0),
        (1, 0, 1),
        (0, 1, 1),
        (100, 200, 300),
        (0.1, 0.2, 0.3),
        (-5, 5, 0)
    ])
    def test_add_parametrized(self, calc, a, b, expected):
        """Параметризованный тест сложения"""
        result = calc.add(a, b)
        assert result == pytest.approx(expected, rel=1e-9)
    
    # ============== Тесты вычитания ==============
    
    def test_subtract_positive_numbers(self, calc):
        """Тест вычитания положительных чисел"""
        assert calc.subtract(10, 5) == 5
        assert calc.subtract(100, 50) == 50
    
    def test_subtract_negative_result(self, calc):
        """Тест вычитания с отрицательным результатом"""
        assert calc.subtract(5, 10) == -5
        assert calc.subtract(0, 10) == -10
    
    # ============== Тесты умножения ==============
    
    @pytest.mark.smoke
    def test_multiply_basic(self, calc):
        """Базовый тест умножения (smoke test)"""
        assert calc.multiply(2, 3) == 6
        assert calc.multiply(5, 4) == 20
    
    def test_multiply_by_zero(self, calc):
        """Тест умножения на ноль"""
        assert calc.multiply(100, 0) == 0
        assert calc.multiply(0, 100) == 0
    
    def test_multiply_negative_numbers(self, calc):
        """Тест умножения отрицательных чисел"""
        assert calc.multiply(-2, 3) == -6
        assert calc.multiply(-2, -3) == 6
    
    # ============== Тесты деления ==============
    
    def test_divide_positive_numbers(self, calc):
        """Тест деления положительных чисел"""
        assert calc.divide(10, 2) == 5
        assert calc.divide(100, 4) == 25
    
    def test_divide_with_float_result(self, calc):
        """Тест деления с дробным результатом"""
        assert calc.divide(10, 3) == pytest.approx(3.333333, rel=1e-5)
        assert calc.divide(7, 2) == 3.5
    
    def test_divide_by_zero_raises_error(self, calc):
        """Тест деления на ноль - должно выбрасывать исключение"""
        with pytest.raises(ValueError) as exc_info:
            calc.divide(10, 0)
        
        assert "Division by zero" in str(exc_info.value)
    
    # ============== Тесты возведения в степень ==============
    
    @pytest.mark.parametrize("base, exp, expected", [
        (2, 3, 8),
        (5, 2, 25),
        (10, 0, 1),
        (2, -1, 0.5),
        (9, 0.5, 3)
    ])
    def test_power(self, calc, base, exp, expected):
        """Тест возведения в степень"""
        assert calc.power(base, exp) == pytest.approx(expected)


class TestCalculatorEdgeCases:
    """Тесты граничных случаев"""
    
    @pytest.fixture
    def calc(self):
        return Calculator()
    
    def test_operations_with_large_numbers(self, calc):
        """Тест операций с большими числами"""
        large_num = 10**10
        assert calc.add(large_num, large_num) == 2 * large_num
        assert calc.multiply(large_num, 2) == 2 * large_num
    
    def test_operations_with_floats(self, calc):
        """Тест операций с числами с плавающей точкой"""
        assert calc.add(0.1, 0.2) == pytest.approx(0.3)
        assert calc.multiply(0.1, 0.1) == pytest.approx(0.01)
    
    @pytest.mark.slow
    def test_many_operations(self, calc):
        """Тест множественных операций (медленный тест)"""
        result = 0
        for i in range(1000):
            result = calc.add(result, i)
        
        # Сумма чисел от 0 до 999 = 999 * 1000 / 2
        expected = 999 * 1000 / 2
        assert result == expected


# ============== Примеры использования маркеров ==============

@pytest.mark.skip(reason="Функциональность еще не реализована")
def test_advanced_calculator_features():
    """Тест расширенных функций калькулятора"""
    pass


@pytest.mark.skipif(not hasattr(Calculator, 'sqrt'), reason="Метод sqrt не реализован")
def test_square_root():
    """Тест квадратного корня"""
    calc = Calculator()
    assert calc.sqrt(9) == 3


@pytest.mark.xfail(reason="Известная проблема с точностью float")
def test_float_precision():
    """Тест точности операций с float (ожидаемый провал)"""
    calc = Calculator()
    # Этот тест провалится из-за особенностей float
    assert calc.add(0.1, 0.2) == 0.3  # На самом деле будет 0.30000000000000004