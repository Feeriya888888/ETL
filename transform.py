"""Transform: очистка, дедупликация, обогащение, витрина."""
import re
import pandas as pd

from src.etl_config import REVENUE_STATUSES, RU_MONTH_FORMAT

CURRENCY_PATTERN = re.compile(r"[^0-9,\.]")


def parse_amount(raw: str):
    """'1 250,50 руб.' -> 1250.5; грязные значения -> None."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    m = re.search(r"\d[\d\s]*(?:[.,]\d+)?", str(raw))
    if not m:
        return None
    num = m.group().replace(" ", "").replace(",", ".")
    try:
        return float(num)
    except ValueError:
        return None


def parse_date(raw: str):
    """'12.03.2025' -> '2025-03-12'; нераспознанное -> None."""
    if not isinstance(raw, str):
        return None
    try:
        return pd.to_datetime(raw, format=RU_MONTH_FORMAT).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return pd.to_datetime(raw, errors="coerce")


def normalize_text(value: str) -> str:
    """Приводит категории и города к единому виду: 'эЛЕКТРОНИКА' -> 'Электроника'."""
    if not isinstance(value, str):
        return ""
    s = value.strip().lower()
    # каждое слово с заглавной буквы
    return " ".join(w.capitalize() for w in s.split())


def deduplicate_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Оставляет последнюю версию каждого заказа по updated_at."""
    df = df.copy()
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")
    df = df.sort_values("updated_at")
    df = df.drop_duplicates(subset="order_id", keep="last")
    return df.drop(columns=["updated_at"])


def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Полный набор правил очистки для продаж."""
    out = df.copy()
    out["amount"] = out["amount_raw"].apply(parse_amount)
    out["order_date"] = out["order_date"].apply(parse_date)
    out["category"] = out["category"].apply(normalize_text)
    out["customer_id"] = out["customer_id"].astype(str).str.strip().str.upper()
    out = deduplicate_sales(out)
    # выбрасываем строки без суммы или без даты — их нельзя посчитать
    out = out.dropna(subset=["amount"])
    return out.reset_index(drop=True)


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Очистка справочника клиентов."""
    out = df.copy()
    out["customer_id"] = out["customer_id"].astype(str).str.strip().str.upper()
    out["city"] = out["city"].apply(normalize_text)
    out["segment"] = out["segment"].apply(lambda s: normalize_text(s) if isinstance(s, str) else "")
    return out


def enrich(sales: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Обогащение: джойн продаж со справочником клиентов (left join)."""
    return sales.merge(customers, on="customer_id", how="left")


def build_mart(df: pd.DataFrame) -> pd.DataFrame:
    """Витрина: выручка по месяцам x категориям x сегментам.

    Учитываются только успешные заказы (статус в REVENUE_STATUSES).
    """
    rev = df[df["status"].isin(REVENUE_STATUSES)].copy()
    if rev.empty:
        return pd.DataFrame(columns=["month", "category", "segment", "orders", "revenue"])
    rev["month"] = pd.to_datetime(rev["order_date"]).dt.strftime("%Y-%m")
    mart = (
        rev.groupby(["month", "category", "segment"], dropna=False)
        .agg(orders=("order_id", "nunique"), revenue=("amount", "sum"))
        .reset_index()
        .sort_values(["month", "category", "segment"])
        .reset_index(drop=True)
    )
    mart["revenue"] = mart["revenue"].round(2)
    return mart
