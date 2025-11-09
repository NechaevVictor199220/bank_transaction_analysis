"""
Модуль сервисов для анализа транзакций.
"""

import logging
import re
from collections import defaultdict
from typing import Any, Dict, List

from src.utils import parse_date

logger = logging.getLogger(__name__)


def profitable_cashback_categories(data: List[Dict], year: int, month: int) -> Dict[str, Any]:
    """
    Сервис 'Выгодные категории повышенного кешбэка'.

    Args:
        data: Список транзакций
        year: Год для анализа
        month: Месяц для анализа

    Returns:
        Dict с категориями кешбэка
    """
    try:
        monthly_transactions = [
            t
            for t in data
            if parse_date(t["Дата операции"]).year == year and parse_date(t["Дата операции"]).month == month
        ]

        # Анализ категорий трат
        category_cashback: Dict[str, float] = defaultdict(float)
        for transaction in monthly_transactions:
            if transaction.get("Сумма платежа", 0) > 0:  # Только траты
                category = transaction.get("Категория", "Другое")
                amount = transaction.get("Сумма платежа", 0)
                cashback = amount * 0.01  # 1% кешбэк
                category_cashback[category] += cashback

        # Сортировка по убыванию кешбэка
        profitable_categories = {
            category: round(cashback, 2)
            for category, cashback in sorted(category_cashback.items(), key=lambda x: x[1], reverse=True)
        }

        response = {"year": year, "month": month, "profitable_categories": profitable_categories}

        logger.info(f"Кешбэк категории рассчитаны для {month}/{year}")
        return response

    except Exception as e:
        logger.error(f"Ошибка расчета кешбэк категорий: {e}")
        return {"error": str(e)}


def investment_piggy_bank(month: str, transactions: List[Dict], limit: int) -> Dict[str, Any]:
    """
    Сервис 'Инвесткопилка'.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Предел округления

    Returns:
        Dict с суммой для инвесткопилки
    """
    try:
        target_year, target_month = map(int, month.split("-"))
        total_rounding = 0

        for transaction in transactions:
            trans_date = parse_date(transaction["Дата операции"])
            if (
                trans_date.year == target_year
                and trans_date.month == target_month
                and transaction.get("Сумма операции", 0) > 0
            ):

                amount = transaction["Сумма операции"]
                rounded_amount = ((amount + limit - 1) // limit) * limit
                rounding = rounded_amount - amount
                total_rounding += rounding

        response = {"month": month, "rounding_limit": limit, "total_savings": round(total_rounding, 2)}

        logger.info(f"Инвесткопилка рассчитана для {month}")
        return response

    except Exception as e:
        logger.error(f"Ошибка расчета инвесткопилки: {e}")
        return {"error": str(e)}


def simple_search(search_query: str, transactions: List[Dict]) -> Dict[str, Any]:
    """
    Сервис 'Простой поиск' по транзакциям.

    Args:
        search_query: Строка для поиска
        transactions: Список транзакций

    Returns:
        Dict с результатами поиска
    """
    try:
        results = [
            t
            for t in transactions
            if (
                search_query.lower() in str(t.get("Описание", "")).lower()
                or search_query.lower() in str(t.get("Категория", "")).lower()
            )
        ]

        response = {
            "search_query": search_query,
            "results_count": len(results),
            "transactions": results[:20],  # Ограничиваем вывод
        }

        logger.info(f"Простой поиск выполнен: '{search_query}'")
        return response

    except Exception as e:
        logger.error(f"Ошибка простого поиска: {e}")
        return {"error": str(e)}


def phone_search(transactions: List[Dict]) -> Dict[str, Any]:
    """
    Сервис 'Поиск по телефонным номерам'.

    Args:
        transactions: Список транзакций

    Returns:
        Dict с найденными телефонными номерами
    """
    try:
        phone_pattern = re.compile(r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
        phone_transactions = []

        for transaction in transactions:
            description = str(transaction.get("Описание", ""))
            phones = phone_pattern.findall(description)
            if phones:
                phone_transactions.append({**transaction, "found_phones": phones})

        response = {"transactions_with_phones": phone_transactions, "total_found": len(phone_transactions)}

        logger.info(f"Найдено транзакций с телефонами: {len(phone_transactions)}")
        return response

    except Exception as e:
        logger.error(f"Ошибка поиска по телефонам: {e}")
        return {"error": str(e)}


def personal_transfers_search(transactions: List[Dict]) -> Dict[str, Any]:
    """
    Сервис 'Поиск переводов физическим лицам'.

    Args:
        transactions: Список транзакций

    Returns:
        Dict с переводами физлицам
    """
    try:
        name_pattern = re.compile(r"[А-Я][а-я]+\s[А-Я]\.")
        personal_transfers = []

        for transaction in transactions:
            category = transaction.get("Категория", "")
            description = str(transaction.get("Описание", ""))

            if category == "Переводы" and name_pattern.search(description):
                personal_transfers.append(transaction)

        response = {"personal_transfers": personal_transfers, "total_found": len(personal_transfers)}

        logger.info(f"Найдено переводов физлицам: {len(personal_transfers)}")
        return response

    except Exception as e:
        logger.error(f"Ошибка поиска переводов физлицам: {e}")
        return {"error": str(e)}
