"""
Модуль отчетов для анализа транзакций.
"""

import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional

import pandas as pd

from src.utils import parse_date

logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для записи результатов отчетов в файл.

    Args:
        filename: Имя файла для записи (опционально)

    Returns:
        Декорированную функцию
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            # Генерация имени файла
            if filename is None:
                report_filename = f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                report_filename = filename

            # Запись в файл
            try:
                with open(report_filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Отчет сохранен в файл: {report_filename}")
            except Exception as e:
                logger.error(f"Ошибка сохранения отчета: {e}")

            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Отчет 'Траты по категории' за последние 3 месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Категория для анализа
        date: Дата отсчета (по умолчанию текущая дата)

    Returns:
        Dict с тратами по категории
    """
    try:
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        start_date = end_date - timedelta(days=90)

        # Создаем копию и работаем с ней, чтобы избежать предупреждения
        transactions_copy = transactions.copy()
        transactions_copy["date"] = transactions_copy["Дата операции"].apply(parse_date)

        # Фильтрация данных
        mask = (
            (transactions_copy["date"] >= start_date)
            & (transactions_copy["date"] <= end_date)
            & (transactions_copy["Категория"] == category)
            & (transactions_copy["Сумма платежа"] > 0)
        )
        filtered_data = transactions_copy.loc[mask].copy()  # Явное копирование

        # Группировка по месяцам
        filtered_data.loc[:, "month"] = filtered_data["date"].dt.to_period("M")
        monthly_spending = filtered_data.groupby("month")["Сумма платежа"].sum()

        result = {
            "category": category,
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "monthly_spending": {str(month): round(amount, 2) for month, amount in monthly_spending.items()},
            "total_spent": round(monthly_spending.sum(), 2),
        }

        logger.info(f"Отчет по категории '{category}' сгенерирован")
        return result

    except Exception as e:
        logger.error(f"Ошибка генерации отчета по категории: {e}")
        return {"error": str(e)}


@report_decorator()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Отчет 'Траты по дням недели' за последние 3 месяца.

    Args:
        transactions: DataFrame с транзакциями
        date: Дата отсчета (по умолчанию текущая дата)

    Returns:
        Dict со средними тратами по дням недели
    """
    try:
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        start_date = end_date - timedelta(days=90)

        # Создаем копию и работаем с ней
        transactions_copy = transactions.copy()
        transactions_copy["date"] = transactions_copy["Дата операции"].apply(parse_date)

        # Фильтрация данных
        mask = (
            (transactions_copy["date"] >= start_date)
            & (transactions_copy["date"] <= end_date)
            & (transactions_copy["Сумма платежа"] > 0)
        )
        filtered_data = transactions_copy.loc[mask].copy()

        # Анализ по дням недели
        filtered_data.loc[:, "weekday"] = filtered_data["date"].dt.day_name()
        weekday_spending = filtered_data.groupby("weekday")["Сумма платежа"].mean()

        # Русские названия дней недели
        russian_days = {
            "Monday": "Понедельник",
            "Tuesday": "Вторник",
            "Wednesday": "Среда",
            "Thursday": "Четверг",
            "Friday": "Пятница",
            "Saturday": "Суббота",
            "Sunday": "Воскресенье",
        }

        # Преобразуем Series в словарь и обрабатываем
        weekday_dict = weekday_spending.to_dict()

        average_spending = {}
        for day, amount in weekday_dict.items():
            russian_day = russian_days.get(day, day)
            average_spending[russian_day] = round(float(amount), 2)

        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "average_spending_by_weekday": average_spending,
        }

        logger.info("Отчет по дням недели сгенерирован")
        return result

    except Exception as e:
        logger.error(f"Ошибка генерации отчета по дням недели: {e}")
        return {"error": str(e)}


@report_decorator()
def spending_workday_weekend(transactions: pd.DataFrame, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Отчет 'Траты в рабочий/выходной день' за последние 3 месяца.

    Args:
        transactions: DataFrame с транзакциями
        date: Дата отсчета (по умолчанию текущая дата)

    Returns:
        Dict со средними тратами в рабочие и выходные дни
    """
    try:
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        start_date = end_date - timedelta(days=90)

        # Создаем копию и работаем с ней
        transactions_copy = transactions.copy()
        transactions_copy["date"] = transactions_copy["Дата операции"].apply(parse_date)

        # Фильтрация данных
        mask = (
            (transactions_copy["date"] >= start_date)
            & (transactions_copy["date"] <= end_date)
            & (transactions_copy["Сумма платежа"] > 0)
        )
        filtered_data = transactions_copy.loc[mask].copy()

        # Определение рабочих и выходных дней
        filtered_data.loc[:, "is_weekend"] = filtered_data["date"].dt.weekday >= 5
        day_type_spending = filtered_data.groupby("is_weekend")["Сумма платежа"].mean()

        # Исправленная строка - явное приведение типов
        workdays_series = day_type_spending.get(False)
        weekends_series = day_type_spending.get(True)

        workdays_value = float(workdays_series) if workdays_series is not None else 0.0
        weekends_value = float(weekends_series) if weekends_series is not None else 0.0

        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "average_spending": {"workdays": round(workdays_value, 2), "weekends": round(weekends_value, 2)},
        }

        logger.info("Отчет по рабочим/выходным дням сгенерирован")
        return result

    except Exception as e:
        logger.error(f"Ошибка генерации отчета по рабочим/выходным дням: {e}")
        return {"error": str(e)}
