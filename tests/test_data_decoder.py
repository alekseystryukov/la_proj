from la_proj.data.decoder import to_native
from datetime import datetime
import unittest


class DateDecoderTestCase(unittest.TestCase):

    def test_apple_market_day(self):
        inputs = (
            "CgRBQVBMFexhnUMYkI6yi8VcKgNOTVMwCDgBRW68EkBItJzfEGXAwuFA2AEE",
            "CgRBQVBMFR9lnUMYoNyyi8VcKgNOTVMwCDgBRYJBE0BI5J7fEGWAj+JA2AEE"
        )
        expected_results = (
            {
                'id': 'AAPL',
                'price': 314.7650146484375,
                'time': datetime(2020, 5, 18, 16, 55, 33),
                'exchange': 'NMS',
                'quoteType': 'EQUITY',
                'marketHours': 'REGULAR_MARKET',
                'changePercent': 2.292750835418701,
                'dayVolume': 35114548,
                'change': 7.055023193359375,
                'priceHint': '4'
            },
            {
                'id': 'AAPL',
                'price': 314.7900085449219,
                'time': datetime(2020, 5, 18, 16, 55, 38),
                'exchange': 'NMS',
                'quoteType': 'EQUITY',
                'marketHours': 'REGULAR_MARKET',
                'changePercent': 2.300873279571533,
                'dayVolume': 35114852,
                'change': 7.08001708984375,
                'priceHint': '4'
            }
        )

        for n, l in enumerate(inputs):
            result = to_native(l)
            self.assertEqual(result, expected_results[n])

