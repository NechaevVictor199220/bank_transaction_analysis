"""
Тесты для модуля utils.
"""
import pytest
import sys
import os
from unittest.mock import patch
import pandas as pd

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    get_greeting_by_time,
    get_exchange_rates,
    get_stock_prices,
    get_date_range
)


class TestUtils:
    """Тесты для модуля utils."""

    @pytest.mark.parametrize("date_time,expected_greeting", [
        ("2024-03-15 08:30:00", "Доброе утро"),
        ("2024-03-15 14:30:00", "Добрый день"),
        ("2024-03-15 20:30:00", "Добрый вечер"),
        ("2024-03-15 02:30:00", "Доброй ночи")
    ])
    def test_get_greeting_by_time(self, date_time: str, expected_greeting: str) -> None:
        """Тест определения приветствия по времени."""
        result = get_greeting_by_time(date_time)
        assert result == expected_greeting

    def test_get_exchange_rates(self) -> None:
        """Тест получения курсов валют."""
        currencies = ["USD", "EUR"]
        result = get_exchange_rates(currencies)
        assert isinstance(result, list)
        assert len(result) <= len(currencies)

    def test_get_stock_prices(self) -> None:
        """Тест получения цен акций."""
        stocks = ["AAPL", "AMZN"]
        result = get_stock_prices(stocks)
        assert isinstance(result, list)
        assert len(result) <= len(stocks)

    @pytest.mark.parametrize("date_str,period", [
        ("2024-03-15 14:30:00", "M"),
        ("2024-03-15 14:30:00", "W"),
        ("2024-03-15 14:30:00", "Y"),
        ("2024-03-15 14:30:00", "ALL")
    ])
    def test_get_date_range(self, date_str: str, period: str) -> None:
        """Тест определения диапазона дат."""
        start_date, end_date = get_date_range(date_str, period)
        assert start_date <= end_date