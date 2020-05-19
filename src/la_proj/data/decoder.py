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


def import_default(value):
    pass


def import_float(value):
    if not value.startswith("0x"):
        return value
    return struct.unpack('!f', bytes.fromhex(value[2:]))[0]


fields = (
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


def normalize_value(value):
    if value.startswith('"'):
        return value.strip('"')
    elif value.startswith("0x"):
        return struct.unpack('!f', bytes.fromhex(value[2:]))[0]

    try:
        dt = datetime.fromtimestamp(int(value) / 2000)
    except ValueError:
        pass
    else:
        if 2019 < dt.year < 2050:
            return dt

    return value


def to_native(msg):
    obj = {}
    for line in msg.split("\n"):
        parts = line.split(": ", 1)
        if len(parts) == 2:
            index, value = parts
            obj[
                fields[int(index) - 1]
            ] = normalize_value(value)
