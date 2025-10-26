"""
Тесты для модуля services.
"""
import pytest
import sys
import os
from unittest.mock import patch

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services import (
    profitable_cashback_categories,
    investment_piggy_bank,
    simple_search,
    phone_search,
    personal_transfers_search
)


class TestServices:
    """Тесты для модуля services."""

    @pytest.fixture
    def sample_transactions(self) -> list[dict]:
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                'Дата операции': '2024-03-15',
                'Сумма операции': 1000.0,
                'Сумма платежа': 1000.0,
                'Категория': 'Продукты',
                'Описание': 'Покупка в магазине'
            },
            {
                'Дата операции': '2024-03-14',
                'Сумма операции': 500.0,
                'Сумма платежа': 500.0,
                'Категория': 'Развлечения',
                'Описание': 'Кинотеатр'
            }
        ]

    def test_profitable_cashback_categories(self, sample_transactions: list[dict]) -> None:
        """Тест сервиса выгодных категорий кешбэка."""
        result = profitable_cashback_categories(sample_transactions, 2024, 3)
        assert "profitable_categories" in result
        assert result["year"] == 2024
        assert result["month"] == 3

    def test_simple_search(self, sample_transactions: list[dict]) -> None:
        """Тест простого поиска."""
        result = simple_search("магазин", sample_transactions)
        assert result["search_query"] == "магазин"
        assert result["results_count"] >= 0

    def test_phone_search(self, sample_transactions: list[dict]) -> None:
        """Тест поиска по телефонным номерам."""
        transactions_with_phones = sample_transactions + [{
            'Дата операции': '2024-03-10',
            'Сумма операции': 100.0,
            'Сумма платежа': 100.0,
            'Категория': 'Связь',
            'Описание': 'Пополнение телефона +7 921 123-45-67'
        }]

        result = phone_search(transactions_with_phones)
        assert "transactions_with_phones" in result

    def test_personal_transfers_search(self, sample_transactions: list[dict]) -> None:
        """Тест поиска переводов физлицам."""
        transfers_with_names = sample_transactions + [{
            'Дата операции': '2024-03-10',
            'Сумма операции': 1000.0,
            'Сумма платежа': 1000.0,
            'Категория': 'Переводы',
            'Описание': 'Перевод Ивану И.'
        }]

        result = personal_transfers_search(transfers_with_names)
        assert "personal_transfers" in result