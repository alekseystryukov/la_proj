from pythonjsonlogger import jsonlogger
import logging
import pytz
import os


WS_ENDPOINT = "wss://streamer.finance.yahoo.com/"
WS_SESSION_HEADER = {
    "Accept-Encoding": "gzip deflat,br",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,uk;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "Upgrade",
    "Host": "streamer.finance.yahoo.com",
    "Origin": "https://finance.yahoo.com",
    "Pragma": "no-cache",
    "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
    "Sec-WebSocket-Key": "5615CFupIMcf4kicVoWPEA==",
    "Sec-WebSocket-Version": "13",
    "Upgrade": "websocket",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/81.0.4044.138 Safari/537.36"
}


API_PORT = int(os.environ.get("API_PORT", 8000))
TZ = pytz.timezone(os.environ.get("TZ", "Europe/Kiev"))
USER_AGENT = os.environ.get("USER_AGENT", "Auction 2.0")
TEST_MODE = os.environ.get("TEST_MODE", False)


MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://root:example@mongo:27017")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "finance")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "symbols")
MONGODB_MINUTE_COLLECTION = os.environ.get("MONGODB_COLLECTION", "minute_data")
MONGODB_WRITE_CONCERN = os.environ.get("MONGODB_WRITE_CONCERN", "majority")
MONGODB_ERROR_INTERVAL = int(os.environ.get("MONGODB_ERROR_INTERVAL", "2"))


# logging
LOGGER_NAME = os.environ.get("LOGGER_NAME", "LA_PRO")
LOG_LEVEL = int(os.environ.get("LOG_LEVEL", logging.INFO))
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOG_LEVEL)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(levelname)s %(asctime)s %(module)s %(process)d '
    '%(message)s %(pathname)s $(lineno)d $(funcName)s'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


FUTURES_SYMBOLS = ("^RUT", "^IXIC", "^DJI", "^GSPC")




