"""Load: запись DataFrame в SQLite. Идемпотентно — таблицы пересоздаются."""
import sqlite3
import pandas as pd

from etl_config import DB_PATH


def load_table(df: pd.DataFrame, table_name: str, db_path=DB_PATH) -> int:
    """Перезаписывает таблицу данными из DataFrame. Возвращает число строк."""
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        return len(df)
    finally:
        conn.close()


def load_all(stg_sales, dim_customers, mart_sales_monthly, db_path=DB_PATH):
    rows = {
        "stg_sales": load_table(stg_sales, "stg_sales", db_path),
        "dim_customers": load_table(dim_customers, "dim_customers", db_path),
        "mart_sales_monthly": load_table(mart_sales_monthly, "mart_sales_monthly", db_path),
    }
    print(f"[load] записано строк: {rows}")
    return rows
