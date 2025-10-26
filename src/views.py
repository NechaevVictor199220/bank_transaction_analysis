"""
Модуль для генерации JSON данных для веб-страниц.
"""

import logging
from typing import Any, Dict

import pandas as pd

from src.utils import (
    get_date_range,
    get_exchange_rates,
    get_greeting_by_time,
    get_stock_prices,
    load_user_settings,
    parse_date,
)

logger = logging.getLogger(__name__)


def home_page(date_time: str) -> Dict[str, Any]:
    """
    Генерирует JSON для главной страницы.

    Args:
        date_time: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS

    Returns:
        Dict с данными для главной страницы
    """
    try:
        # Загрузка данных
        df = pd.read_excel("data/operations.xlsx")
        start_date, end_date = get_date_range(date_time, "M")

        # Фильтрация данных за текущий месяц с правильным парсингом дат
        df["date"] = df["Дата операции"].apply(parse_date)
        monthly_data = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        # Приветствие
        greeting = get_greeting_by_time(date_time)

        # Анализ по картам
        cards_analysis = []
        if "Номер карты" in monthly_data.columns:
            for card in monthly_data["Номер карты"].unique():
                if pd.notna(card):  # Проверяем что значение не NaN
                    card_data = monthly_data[monthly_data["Номер карты"] == card]
                    total_spent = card_data[card_data["Сумма платежа"] > 0]["Сумма платежа"].sum()
                    cashback = total_spent * 0.01  # 1% кешбэк

                    cards_analysis.append(
                        {
                            "last_digits": str(card)[-4:],
                            "total_spent": round(total_spent, 2),
                            "cashback": round(cashback, 2),
                        }
                    )

        # Топ-5 транзакций
        top_transactions = []
        if not monthly_data.empty:
            # Берем топ-5 по абсолютной величине (самые крупные траты и поступления)
            top_5 = monthly_data.nlargest(5, "Сумма платежа")
            for _, transaction in top_5.iterrows():
                top_transactions.append(
                    {
                        "date": transaction["date"].strftime("%d.%m.%Y"),
                        "amount": float(transaction["Сумма платежа"]),
                        "category": str(transaction.get("Категория", "Не указана")),
                        "description": str(transaction.get("Описание", "Без описания")),
                    }
                )

        # Курсы валют и акции
        user_settings = load_user_settings()
        currency_rates = get_exchange_rates(user_settings.get("user_currencies", []))
        stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

        response = {
            "greeting": greeting,
            "cards": cards_analysis,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        logger.info(f"Главная страница сгенерирована для {date_time}")
        return response

    except Exception as e:
        logger.error(f"Ошибка генерации главной страницы: {e}")
        return {"error": str(e)}


def events_page(date_time: str, period: str = "M") -> Dict[str, Any]:
    """
    Генерирует JSON для страницы событий.

    Args:
        date_time: Строка с датой и временем
        period: Период анализа ('W', 'M', 'Y', 'ALL')

    Returns:
        Dict с данными для страницы событий
    """
    try:
        # Загрузка данных
        df = pd.read_excel("data/operations.xlsx")
        start_date, end_date = get_date_range(date_time, period)

        # Фильтрация данных с правильным парсингом дат
        df["date"] = df["Дата операции"].apply(parse_date)
        period_data = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        # Анализ расходов (положительные суммы)
        expenses_data = period_data[period_data["Сумма платежа"] > 0]
        total_expenses = expenses_data["Сумма платежа"].sum()

        # Анализ по категориям расходов
        expenses_by_category = expenses_data.groupby("Категория")["Сумма платежа"].sum()
        main_expenses = []
        other_amount = 0

        for i, (category, amount) in enumerate(expenses_by_category.nlargest(7).items()):
            if i < 6:
                main_expenses.append({"category": str(category), "amount": round(amount)})
            else:
                other_amount += amount

        if other_amount > 0:
            main_expenses.append({"category": "Остальное", "amount": round(other_amount)})

        # Переводы и наличные
        transfers_cash_categories = ["Наличные", "Переводы"]
        transfers_and_cash = []

        for category in transfers_cash_categories:
            if category in expenses_by_category.index:
                transfers_and_cash.append({"category": category, "amount": round(expenses_by_category[category])})

        # Анализ поступлений (отрицательные суммы)
        income_data = period_data[period_data["Сумма платежа"] < 0]
        total_income = abs(income_data["Сумма платежа"].sum())

        income_by_category = income_data.groupby("Категория")["Сумма платежа"].sum().abs()
        main_income = []

        for category, amount in income_by_category.nlargest(5).items():
            main_income.append({"category": str(category), "amount": round(amount)})

        # Курсы валют и акции
        user_settings = load_user_settings()
        currency_rates = get_exchange_rates(user_settings.get("user_currencies", []))
        stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

        response = {
            "expenses": {
                "total_amount": round(total_expenses),
                "main": main_expenses,
                "transfers_and_cash": transfers_and_cash,
            },
            "income": {"total_amount": round(total_income), "main": main_income},
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        logger.info(f"Страница событий сгенерирована для периода {period}")
        return response

    except Exception as e:
        logger.error(f"Ошибка генерации страницы событий: {e}")
        return {"error": str(e)}
