"""Extract: чтение исходников в pandas DataFrame."""
import json
import pandas as pd

from etl_config import SALES_CSV, CUSTOMERS_JSON


def extract_sales(path=SALES_CSV) -> pd.DataFrame:
    """Читает сырые продажи из CSV."""
    df = pd.read_csv(path, dtype={"order_id": str, "customer_id": str})
    required = {"order_id", "customer_id", "order_date", "amount_raw", "category", "status", "updated_at"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"В sales.csv нет колонок: {sorted(missing)}")
    return df


def extract_customers(path=CUSTOMERS_JSON) -> pd.DataFrame:
    """Читает справочник клиентов из JSON (имитация ответа API)."""
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    return pd.DataFrame(records)
