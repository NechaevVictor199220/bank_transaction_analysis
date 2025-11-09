"""
Тесты для модуля reports.
"""
import pytest
import sys
import os
import pandas as pd
from unittest.mock import patch

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_workday_weekend
)


class TestReports:
    """Тесты для модуля reports."""

    @pytest.fixture
    def sample_dataframe(self) -> pd.DataFrame:
        """Фикстура с тестовым DataFrame."""
        return pd.DataFrame({
            'Дата операции': [
                '2024-01-15', '2024-02-10', '2024-03-05',
                '2024-01-20', '2024-02-15', '2024-03-10'
            ],
            'Сумма платежа': [1000.0, 1500.0, 800.0, 1200.0, 900.0, 600.0],
            'Категория': [
                'Продукты', 'Продукты', 'Продукты',
                'Развлечения', 'Развлечения', 'Развлечения'
            ]
        })

    def test_spending_by_category(self, sample_dataframe: pd.DataFrame) -> None:
        """Тест отчета по категории."""
        result = spending_by_category(sample_dataframe, "Продукты", "2024-03-15")
        assert "category" in result
        assert "total_spent" in result
        assert result["category"] == "Продукты"

    def test_spending_by_weekday(self, sample_dataframe: pd.DataFrame) -> None:
        """Тест отчета по дням недели."""
        result = spending_by_weekday(sample_dataframe, "2024-03-15")
        assert "average_spending_by_weekday" in result
        assert "period" in result

    def test_spending_workday_weekend(self, sample_dataframe: pd.DataFrame) -> None:
        """Тест отчета по рабочим/выходным дням."""
        result = spending_workday_weekend(sample_dataframe, "2024-03-15")
        assert "average_spending" in result
        assert "workdays" in result["average_spending"]
        assert "weekends" in result["average_spending"]