from collections import deque
from datetime import timedelta
from collections import defaultdict
import logging


logger = logging.getLogger(__name__)


class DataProcessor:

    all_functions = ("peaks",)
    results: dict  # store calculated results here
    data: dict

    def __init__(self, functions=None):
        if functions:
            self.all_functions = [f for f in DataProcessor.all_functions
                                  if f in functions]
        self.results = defaultdict(dict)
        self.data = defaultdict(lambda: deque(maxlen=60 * 24 * 2))

    def get_result(self, symbol, function):
        symbol_results = self.results.get(symbol)
        if symbol_results:
            return symbol_results.get(function)

    def calculate_functions(self, symbol, new_data):
        self.merge_data(self.data[symbol], new_data)
        for f in self.all_functions:
            try:
                self.results[symbol][f] = getattr(self, f)(
                    self.data[symbol]
                )
            except Exception as e:
                logger.exception(e)

    @staticmethod
    def merge_data(data, updates):
        for update in updates:
            if data:
                for e in reversed(data):
                    # this or the second expected
                    # to happen at the very beginning
                    if e["time"] < update["time"]:
                        data.append(update)
                        break
                    elif e["time"] == update["time"]:
                        e.update(**update)
                        break
            else:
                data.append(update)

    @staticmethod
    def peaks(data):
        min_interval = timedelta(seconds=60 * 2)
        ups = deque(maxlen=2)
        downs = deque(maxlen=2)

        def append_element(queue, t, c):
            if len(queue) > 1 and (t - queue[-1]["time"]) <= min_interval:
                queue[-1] = dict(time=t, close=c)
            else:
                queue.append(dict(time=t, close=c))

        for p in data:
            time, close = p["time"], p["close"]

            if not ups or ups[-1]["close"] < close:
                append_element(ups, time, close)

            if not downs or downs[-1]["close"] > close:
                append_element(downs, time, close)

        # return latest peak
        if ups and downs:
            if ups[-1]["time"] > downs[-1]["time"]:
                result = ups
            else:
                result = downs
        elif ups:
            result = ups
        else:
            result = downs
        return list(result)
