"""Точка входа ETL-пайплайна. Запуск: python main.py"""
import pandas as pd

from src import extract, transform, load


def run():
    print("[extract] читаю источники...")
    sales_raw = extract.extract_sales()
    customers_raw = extract.extract_customers()
    print(f"[extract] продаж: {len(sales_raw)}, клиентов: {len(customers_raw)}")

    print("[transform] очищаю и обогащаю...")
    sales = transform.transform_sales(sales_raw)
    customers = transform.transform_customers(customers_raw)
    enriched = transform.enrich(sales, customers)
    mart = transform.build_mart(enriched)

    print("[load] загружаю в SQLite...")
    load.load_all(sales, customers, mart)

    print("\nВитрина mart_sales_monthly (первые 10 строк):")
    print(mart.head(10).to_string(index=False))


if __name__ == "__main__":
    run()
