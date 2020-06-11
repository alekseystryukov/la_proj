from la_proj.api.functions import DataProcessor
from datetime import datetime
import unittest


class MergeDataAndRunFunctionsTestCase(unittest.TestCase):

    def test_peaks(self):
        function = "peaks"
        processor = DataProcessor(functions=function)
        symbol = "XYZ"
        data = [
            {
                'time': datetime(2020, 5, 18, 16, 40),
                'close': 123,
            },
            {
                'time': datetime(2020, 5, 18, 16, 41),
                'close': 120,
            }
        ]
        self.assertIsNone(processor.get_result(symbol, function))
        processor.calculate_functions(symbol, data)
        self.assertEqual(
            processor.get_result(symbol, function),
            [
                {'time': datetime(2020, 5, 18, 16, 40), 'close': 123},
                {'time': datetime(2020, 5, 18, 16, 41), 'close': 120}
            ]
        )

        # 2
        more_data = [
            {'time': datetime(2020, 5, 18, 16, 42), 'close': 122},
            {'time': datetime(2020, 5, 18, 16, 43), 'close': 122},
            {'time': datetime(2020, 5, 18, 16, 44), 'close': 119}
        ]
        processor.calculate_functions(symbol, more_data)
        self.assertEqual(
            processor.get_result(symbol, function),
            [
                {'time': datetime(2020, 5, 18, 16, 41), 'close': 120},
                {'time': datetime(2020, 5, 18, 16, 44), 'close': 119}
            ]
        )


class HighsAndLowsTestCase(unittest.TestCase):

    def test_high(self):
        data = [
            {
                'time': datetime(2020, 5, 18, 16, 40),
                'close': 123,
            },
            {
                'time': datetime(2020, 5, 18, 16, 41),
                'close': 120,
            },
            {
                'time': datetime(2020, 5, 18, 16, 42),
                'close': 119,
            },
            {
                'time': datetime(2020, 5, 18, 16, 43),
                'close': 120,
            },
            {
                'time': datetime(2020, 5, 18, 16, 44),
                'close': 130,
            },
        ]
        result = DataProcessor.peaks(data)
        self.assertEqual(
            result,
            [
                {
                    "time": datetime(2020, 5, 18, 16, 40),
                    'close': 123,
                },
                {
                    "time": datetime(2020, 5, 18, 16, 44),
                    'close': 130,
                }
            ]
        )

    def test_low(self):
        data = [
                {
                    'time': datetime(2020, 5, 18, 16, 40),
                    'close': 123,
                },
                {
                    'time': datetime(2020, 5, 18, 16, 41),
                    'close': 120,
                },
                {
                    'time': datetime(2020, 5, 18, 16, 42),
                    'close': 123,
                },
                {
                    'time': datetime(2020, 5, 18, 16, 43),
                    'close': 124,
                },
                {
                    'time': datetime(2020, 5, 18, 16, 44),
                    'close': 119,
                },
                {
                    'time': datetime(2020, 5, 18, 16, 45),
                    'close': 118,
                },
                {
                    'time': datetime(2020, 5, 18, 16, 46),
                    'close': 120,
                },
            ]
        result = DataProcessor.peaks(data)
        self.assertEqual(
            result,
            [
                {
                    "time": datetime(2020, 5, 18, 16, 41),
                    'close': 120,
                },
                {
                    "time": datetime(2020, 5, 18, 16, 45),
                    'close': 118,
                }
            ]
        )
