"""
Вспомогательные функции для работы с данными.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd

# Создаем папку logs если она не существует
os.makedirs("logs", exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def load_transactions_from_excel(file_path: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel файла.

    Args:
        file_path: Путь к Excel файлу

    Returns:
        DataFrame с транзакциями
    """
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Транзакции загружены из {file_path}")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        return pd.DataFrame()


def parse_date(date_str: str) -> datetime:
    """
    Парсит дату из строки в формате DD.MM.YYYY HH:MM:SS.

    Args:
        date_str: Строка с датой

    Returns:
        Объект datetime
    """
    try:
        # Пробуем разные форматы дат
        formats = [
            "%d.%m.%Y %H:%M:%S",  # DD.MM.YYYY HH:MM:SS
            "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
            "%d.%m.%Y",  # DD.MM.YYYY
            "%Y-%m-%d",  # YYYY-MM-DD
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Если ни один формат не подошел
        logger.warning(f"Не удалось распарсить дату: {date_str}")
        return datetime.now()

    except Exception as e:
        logger.error(f"Ошибка парсинга даты {date_str}: {e}")
        return datetime.now()


def get_exchange_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает текущие курсы валют через API.

    Args:
        currencies: Список валют для получения курсов

    Returns:
        List с курсами валют
    """
    try:
        # Заглушка для API (в реальности нужно использовать реальное API)
        rates_data = {"USD": 75.0, "EUR": 85.0, "GBP": 95.0}

        rates: List[Dict[str, Any]] = []
        for currency in currencies:
            if currency in rates_data:
                rates.append({"currency": currency, "rate": rates_data[currency]})

        logger.info(f"Курсы валют получены для {currencies}")
        return rates

    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        return []


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает текущие цены акций через API.

    Args:
        stocks: Список акций для получения цен

    Returns:
        List с ценами акций
    """
    try:
        # Заглушка для API (в реальности нужно использовать реальное API)
        prices_data = {"AAPL": 150.12, "AMZN": 3173.18, "GOOGL": 2742.39, "MSFT": 296.71, "TSLA": 1007.08}

        prices: List[Dict[str, Any]] = []
        for stock in stocks:
            if stock in prices_data:
                prices.append({"stock": stock, "price": prices_data[stock]})

        logger.info(f"Цены акций получены для {stocks}")
        return prices

    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        return []


def get_greeting_by_time(date_time: str) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        date_time: Строка с датой и временем в формате YYYY-MM-DD HH:MM:SS

    Returns:
        Строка с приветствием
    """
    try:
        dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour

        if 5 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 18:
            return "Добрый день"
        elif 18 <= hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"

    except Exception as e:
        logger.error(f"Ошибка определения приветствия: {e}")
        return "Добрый день"


def get_date_range(date_str: str, period: str = "M") -> tuple[datetime, datetime]:
    """
    Возвращает диапазон дат для анализа.

    Args:
        date_str: Строка с датой
        period: Период ('W' - неделя, 'M' - месяц, 'Y' - год, 'ALL' - все данные)

    Returns:
        Кортеж (start_date, end_date)
    """
    try:
        end_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        if period == "W":
            start_date = end_date - timedelta(days=end_date.weekday())
        elif period == "M":
            start_date = end_date.replace(day=1)
        elif period == "Y":
            start_date = end_date.replace(month=1, day=1)
        elif period == "ALL":
            start_date = datetime(2000, 1, 1)  # Начальная дата
        else:
            start_date = end_date.replace(day=1)

        return start_date, end_date

    except Exception as e:
        logger.error(f"Ошибка определения диапазона дат: {e}")
        return datetime.now().replace(day=1), datetime.now()


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки из JSON файла.

    Returns:
        Dict с настройками пользователя
    """
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            settings: Dict[str, Any] = json.load(f)
        logger.info("Пользовательские настройки загружены")
        return settings
    except Exception as e:
        logger.error(f"Ошибка загрузки настроек: {e}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}
