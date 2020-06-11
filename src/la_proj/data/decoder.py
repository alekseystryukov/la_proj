from datetime import datetime
import subprocess
import struct
import base64


def decode_msg(msg):
    result = subprocess.check_output(
        ['./libs/protoc', '--decode_raw'],
        input=base64.b64decode(msg)
    ).decode()
    return result


def import_string(value):
    return value.strip('"')


def import_float(value):
    return struct.unpack('!f', bytes.fromhex(value[2:]))[0]


def import_int(value):
    return int(value)


def import_datetime(value):
    try:
        dt = datetime.fromtimestamp(int(value) / 2000)
    except ValueError:
        pass
    else:
        return dt


def default_import(value):
    if value.startswith('"'):
        return import_string(value)
    elif value.startswith("0x"):
        return import_float(value)
    dt = import_datetime(value)
    if dt is not None and 2019 < dt.year < 2050:
        return dt
    return value


def import_quote_type(value):
    return QUOTE_TYPES.get(value, value)


def import_marker_hours(value):
    return MARKET_HOURS.get(value, value)


FIELDS = (
    "id",
    "price",
    "time",
    "currency",
    "exchange",
    "quoteType",
    "marketHours",
    "changePercent",
    "dayVolume",
    "dayHigh",
    "dayLow",
    "change",
    "shortName",
    "expireDate",
    "openPrice",
    "previousClose",
    "strikePrice",
    "underlyingSymbol",
    "openInterest",
    "optionsType",
    "miniOption",
    "lastSize",
    "bid",
    "bidSize",
    "ask",
    "askSize",
    "priceHint",
    "vol_24hr",
    "volAllCurrencies",
    "fromcurrency",
    "lastMarket",
    "circulatingSupply",
    "marketcap",
)

IMPORT_FUNCTIONS = {
    "id": import_string,
    "price": import_float,
    "time": import_datetime,
    "exchange": import_string,
    "changePercent": import_float,
    "change": import_float,
    "dayVolume": import_int,
    "quoteType": import_quote_type,
    "marketHours": import_marker_hours,
}

QUOTE_TYPES = {
    "0": "NONE",
    "5": "ALTSYMBOL",
    "7": "HEARTBEAT",
    "8": "EQUITY",
    "9": "INDEX",
    "11": "MUTUALFUND",
    "12": "MONEYMARKET",
    "13": "OPTION",
    "14": "CURRENCY",
    "15": "WARRANT",
    "17": "BOND",
    "18": "FUTURE",
    "20": "ETF",
    "23": "COMMODITY",
    "28": "ECNQUOTE",
    "41": "CRYPTOCURRENCY",
    "42": "INDICATOR",
    "1000": "INDUSTRY",
}

MARKET_HOURS = {
    "0": "PRE_MARKET",
    "1": "REGULAR_MARKET",
    "2": "POST_MARKET",
    "3": "EXTENDED_HOURS_MARKET",
}


def to_native(msg):
    decoded = decode_msg(msg)
    obj = {}
    for line in decoded.split("\n"):
        parts = line.split(": ", 1)
        if len(parts) == 2:
            index, value = parts
            field_name = FIELDS[int(index) - 1]
            import_func = IMPORT_FUNCTIONS.get(field_name, default_import)
            # print(field_name, value)
            obj[field_name] = import_func(value)
    return obj
