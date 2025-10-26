"""
Тесты для модуля views.
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import pandas as pd

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.views import home_page, events_page


class TestViews:
    """Тесты для модуля views."""

    @pytest.fixture
    def sample_transactions(self) -> pd.DataFrame:
        """Фикстура с тестовыми транзакциями."""
        return pd.DataFrame({
            'Дата операции': ['2024-03-15', '2024-03-14', '2024-03-10'],
            'Номер карты': ['1234567890123456', '1234567890123456', '1234567890123456'],
            'Сумма платежа': [1000.0, -500.0, 200.0],
            'Категория': ['Продукты', 'Зарплата', 'Развлечения'],
            'Описание': ['Покупка в магазине', 'Начисление зарплаты', 'Кино']
        })

    def test_home_page_success(self) -> None:
        """Тест успешной генерации главной страницы."""
        with patch('src.views.pd.read_excel') as mock_read:
            mock_read.return_value = pd.DataFrame({
                'Дата операции': ['2024-03-15'],
                'Номер карты': ['1234567890123456'],
                'Сумма платежа': [1000.0],
                'Категория': ['Продукты'],
                'Описание': ['Тест']
            })

            result = home_page("2024-03-15 14:30:00")
            assert "greeting" in result
            assert "cards" in result
            assert "top_transactions" in result

    def test_events_page_success(self, sample_transactions: pd.DataFrame) -> None:
        """Тест успешной генерации страницы событий."""
        with patch('src.views.pd.read_excel') as mock_read:
            mock_read.return_value = sample_transactions

            result = events_page("2024-03-15 14:30:00", "M")
            assert "expenses" in result
            assert "income" in result
            assert "currency_rates" in result

    @pytest.mark.parametrize("date_time,period", [
        ("2024-03-15 14:30:00", "M"),
        ("2024-03-15 09:00:00", "W"),
        ("2024-03-15 20:00:00", "Y"),
        ("2024-03-15 23:59:59", "ALL")
    ])
    def test_events_page_parametrized(self, date_time: str, period: str, sample_transactions: pd.DataFrame) -> None:
        """Параметризованный тест страницы событий."""
        with patch('src.views.pd.read_excel') as mock_read:
            mock_read.return_value = sample_transactions
            result = events_page(date_time, period)
            assert result.get("expenses") is not None