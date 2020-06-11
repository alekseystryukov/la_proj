from la_proj.storage import get_minute_collection_name
from la_proj.data.storage import update_minute_price, MINUTE_COLLECTION
from la_proj.settings import MONGODB_MINUTE_COLLECTION
from datetime import datetime
import asyncio
import unittest


class StorageTestCase(unittest.TestCase):
    symbol = "OMG"

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.run_until_complete(
            MINUTE_COLLECTION.delete_many({"symbol": self.symbol})
        )

    def test_get_minute_collection_name(self):
        tests = (
            ("AAPL", f"{MONGODB_MINUTE_COLLECTION}_AAPL"),
            ("aapl", f"{MONGODB_MINUTE_COLLECTION}_aapl"),
            ("^FTAI", f"{MONGODB_MINUTE_COLLECTION}__FTAI"),
            ("BTC-GBP", f"{MONGODB_MINUTE_COLLECTION}_BTC_GBP"),
            ("GBPUSD=X", f"{MONGODB_MINUTE_COLLECTION}_GBPUSD_X"),
        )
        for symbol, name in tests:
            result = get_minute_collection_name(symbol)
            self.assertEqual(result, name)

    def test_update_minute_price(self):
        updates = (
            dict(symbol=self.symbol, time=datetime(2020, 5, 18, 16, 58, 00), price=177, volume=12),
            dict(symbol=self.symbol, time=datetime(2020, 5, 18, 16, 58, 33), price=177.01, volume=3),
            dict(symbol=self.symbol, time=datetime(2020, 5, 18, 16, 58, 13), price=12, volume=14),
            dict(symbol=self.symbol, time=datetime(2020, 5, 18, 16, 58, 59), price=150, volume=15),
            dict(symbol=self.symbol, time=datetime(2020, 5, 18, 16, 59, 1), price=200, volume=18),
        )
        for u in updates:
            self.loop.run_until_complete(
                update_minute_price(**u)
            )

        # checks -----
        first = self.loop.run_until_complete(
            MINUTE_COLLECTION.find_one(
                {"symbol": self.symbol, "time": datetime(2020, 5, 18, 16, 58)}
            )
        )
        del first["_id"]
        self.assertEqual(
            first,
            {
                'symbol': self.symbol,
                'time': datetime(2020, 5, 18, 16, 58),
                'close': 177,
                'high': 177,
                'low': 177,
                'open': 177,
                'updated': datetime(2020, 5, 18, 16, 58),
                'updates': 1,
                'volume': 12
            }
        )

        # ----
        second = self.loop.run_until_complete(
            MINUTE_COLLECTION.find_one(
                {"symbol": self.symbol, "time": datetime(2020, 5, 18, 16, 59)}
            )
        )
        del second["_id"]
        self.assertEqual(
            second,
            {
                'symbol': self.symbol,
                'time': datetime(2020, 5, 18, 16, 59),
                'close': 150,
                'high': 177.01,
                'low': 12,
                'open': 177.01,
                'updated': datetime(2020, 5, 18, 16, 58, 59),
                'updates': 3,
                'volume': 15
            }
        )

        # ----
        third = self.loop.run_until_complete(
            MINUTE_COLLECTION.find_one(
                {"symbol": self.symbol, "time": datetime(2020, 5, 18, 17)}
            )
        )
        del third["_id"]
        self.assertEqual(
            third,
            {
                'symbol': self.symbol,
                'time': datetime(2020, 5, 18, 17, 0),
                'close': 200,
                'high': 200,
                'low': 200,
                'open': 200,
                'updated': datetime(2020, 5, 18, 16, 59, 1),
                'updates': 1,
                'volume': 18
            }
        )
