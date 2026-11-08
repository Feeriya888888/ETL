"""Юнит-тесты правил трансформации. Запуск: python -m unittest discover tests -v"""
import unittest

import pandas as pd

from src import transform


class TestParseAmount(unittest.TestCase):
    def test_russian_format(self):
        self.assertEqual(transform.parse_amount("1 250,50 руб."), 1250.5)

    def test_plain_number(self):
        self.assertEqual(transform.parse_amount("450"), 450.0)

    def test_garbage(self):
        self.assertIsNone(transform.parse_amount("н/д"))


class TestNormalizeText(unittest.TestCase):
    def test_shouting_category(self):
        self.assertEqual(transform.normalize_text("эЛЕКТРОНИКА"), "Электроника")

    def test_extra_spaces(self):
        self.assertEqual(transform.normalize_text("  дом   и сад "), "Дом И Сад")


class TestDeduplicate(unittest.TestCase):
    def test_keeps_last_version(self):
        df = pd.DataFrame(
            {
                "order_id": ["1", "1"],
                "updated_at": ["2025-03-12 10:00:00", "2025-03-14 08:00:00"],
                "amount": [100.0, 200.0],
            }
        )
        result = transform.deduplicate_sales(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["amount"], 200.0)


class TestBuildMart(unittest.TestCase):
    def test_canceled_not_in_revenue(self):
        df = pd.DataFrame(
            {
                "order_id": ["1", "2"],
                "order_date": ["2025-03-12", "2025-03-12"],
                "amount": [100.0, 500.0],
                "category": ["Книги", "Книги"],
                "segment": ["Regular", "Regular"],
                "status": ["done", "canceled"],
            }
        )
        mart = transform.build_mart(df)
        self.assertEqual(mart["revenue"].sum(), 100.0)


if __name__ == "__main__":
    unittest.main()
