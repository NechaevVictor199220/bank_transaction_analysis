"""
Основной модуль приложения для анализа транзакций.
Запускает все реализованные функциональности.
"""

from src.reports import spending_by_category, spending_by_weekday, spending_workday_weekend
from src.services import (
    investment_piggy_bank,
    personal_transfers_search,
    phone_search,
    profitable_cashback_categories,
    simple_search,
)
from src.utils import load_transactions_from_excel
from src.views import events_page, home_page


def main() -> None:
    """
    Основная функция приложения.
    Демонстрирует работу всех реализованных функциональностей.
    """
    print("=== Анализ банковских транзакций ===\n")

    try:
        # Загрузка данных
        print("1. Загрузка данных...")
        df = load_transactions_from_excel("data/operations.xlsx")
        transactions = df.to_dict("records")
        print(f"   Загружено {len(transactions)} транзакций")

        # Веб-страницы
        print("\n2. Генерация веб-страниц...")

        # Главная страница
        home_result = home_page("2024-03-15 14:30:00")
        print(
            f"   Главная страница: {len(home_result.get('cards', []))} карт, "
            f"{len(home_result.get('top_transactions', []))} транзакций"
        )

        # Страница событий
        events_result = events_page("2024-03-15 14:30:00", "M")
        print(
            f"   Страница событий: расходы {events_result.get('expenses', {}).get('total_amount', 0)} руб, "
            f"поступления {events_result.get('income', {}).get('total_amount', 0)} руб"
        )

        # Сервисы
        print("\n3. Работа сервисов...")

        # Выгодные категории кешбэка
        cashback_result = profitable_cashback_categories(transactions, 2024, 3)
        print(f"   Кешбэк категории: {len(cashback_result.get('profitable_categories', {}))} категорий")

        # Инвесткопилка
        investment_result = investment_piggy_bank("2024-03", transactions, 10)
        print(f"   Инвесткопилка: {investment_result.get('total_savings', 0)} руб")

        # Простой поиск
        search_result = simple_search("перевод", transactions)
        print(f"   Простой поиск: найдено {search_result.get('results_count', 0)} результатов")

        # Поиск по телефонам
        phone_result = phone_search(transactions)
        print(f"   Поиск по телефонам: найдено {phone_result.get('total_found', 0)} транзакций")

        # Поиск переводов физлицам
        transfers_result = personal_transfers_search(transactions)
        print(f"   Переводы физлицам: найдено {transfers_result.get('total_found', 0)} транзакций")

        # Отчеты
        print("\n4. Генерация отчетов...")

        # Траты по категории
        category_report = spending_by_category(df, "Продукты", "2024-03-15")
        print(f"   Траты по категории: {category_report.get('total_spent', 0)} руб")

        # Траты по дням недели
        weekday_report = spending_by_weekday(df, "2024-03-15")
        print(f"   Траты по дням недели: {len(weekday_report.get('average_spending_by_weekday', {}))} дней")

        # Траты в рабочие/выходные
        workday_report = spending_workday_weekend(df, "2024-03-15")
        workdays = workday_report.get("average_spending", {}).get("workdays", 0)
        weekends = workday_report.get("average_spending", {}).get("weekends", 0)
        print(f"   Траты: рабочие {workdays} руб, выходные {weekends} руб")

        print("\n✅ Все функциональности выполнены успешно!")
        print("\n📊 Результаты сохранены в JSON файлы в текущей директории")

    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")


if __name__ == "__main__":
    main()
