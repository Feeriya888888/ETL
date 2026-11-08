"""Конфигурация пайплайна: пути и константы."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "sales.db"

SALES_CSV = DATA_DIR / "sales.csv"
CUSTOMERS_JSON = DATA_DIR / "customers.json"

# какие статусы заказов считаем выручкой
REVENUE_STATUSES = {"done"}

RU_MONTH_FORMAT = "%d.%m.%Y"  # формат дат в исходном CSV
