from pythonjsonlogger import jsonlogger
import logging
import pytz
import os


WS_ENDPOINT = "wss://streamer.finance.yahoo.com/"
WS_SESSION_HEADER = {
    "Accept-Encoding": "gzip deflat,br",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,zh-CN;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "Upgrade",
    "Host": "streamer.finance.yahoo.com",
    "Origin": "https://finance.yahoo.com",
    "Pragma": "no-cache",
    "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
    "Sec-WebSocket-Key": "VW2m4Lw2Rz2nXaWO10kxhw==",
    "Sec-WebSocket-Version": "13",
    "Upgrade": "websocket",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}


API_PORT = int(os.environ.get("API_PORT", 8000))
TZ = pytz.timezone(os.environ.get("TZ", "Europe/Kiev"))
USER_AGENT = os.environ.get("USER_AGENT", "Auction 2.0")
TEST_MODE = os.environ.get("TEST_MODE", False)


MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "finance")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "symbols")
MONGODB_WRITE_CONCERN = os.environ.get("MONGODB_WRITE_CONCERN", "majority")


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




