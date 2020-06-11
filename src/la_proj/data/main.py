#! /usr/bin/env python
from la_proj.settings import WS_ENDPOINT, WS_SESSION_HEADER, logger
from la_proj.data.decoder import to_native
from la_proj.data.storage import update_minute_price
from la_proj.storage import get_symbols
from datetime import datetime
import argparse
import asyncio
import signal
import random
import aiohttp
import json

RUN = True


async def process_message(msg):
    line = to_native(msg)
    logger.info("Got msg", extra={"DATA": line})
    # if line.get("marketHours") != "REGULAR_MARKET":
    #     return
    # {"id": "AAPL", "price": 316.70001220703125, "time": "2020-05-20T11:54:17",
    # "exchange": "NMS", "quoteType": "EQUITY", "marketHours": "PRE_MARKET",
    # "changePercent": 1.1368708610534668, "change": 3.55999755859375, "priceHint": "4"}
    try:
        upd_kwargs = dict(
            symbol=line["id"],
            time=line["time"],
            price=line["price"],
            volume=line.get("dayVolume", 0),
        )
    except KeyError as e:
        logger.exception(e)
    else:
        await update_minute_price(**upd_kwargs)


def get_stop_signal_handler(sig):
    def handler(signum, frame):
        global RUN
        logger.warning(f"Handling {sig} signal: stopping crawlers", extra={"MESSAGE_ID": "HANDLE_STOP_SIG"})
        RUN = False
    return handler


async def main(symbols):
    if not symbols:
        symbols = [s["id"] for s in await get_symbols()]

    conn = aiohttp.TCPConnector(ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=conn, headers=WS_SESSION_HEADER) as session:
        ws = await session.ws_connect(WS_ENDPOINT)
        msg_data = {"subscribe": symbols}
        await ws.send_str(json.dumps(msg_data))
        logger.info("Sent sub", extra={"MESSAGE": msg_data})
        while RUN:
            msg = await ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                await process_message(msg.data)
            else:
                logger.error(f"Unexpected msg.type {msg}")
                break


async def fake_data_producer(symbols):
    producers = [symbol_data_producer(s) for s in symbols]

    while RUN:
        await asyncio.sleep(0.3)
        for p in producers:
            fake_data = next(p)
            await update_minute_price(**fake_data)


def symbol_data_producer(symbol):
    price = random.randint(2000, 10000)
    while RUN:
        trend = random.choice([1, -1])
        for _ in range(20):
            data = dict(
                symbol=symbol,
                time=datetime.utcnow(),
                price=price,
                volume=random.randint(2000, 10000),
            )
            yield data
            price += trend * random.randint(0, 20)


if __name__ == "__main__":
    # signal.signal(signal.SIGINT, get_stop_signal_handler("SIGINT"))
    # signal.signal(signal.SIGTERM, get_stop_signal_handler("SIGTERM"))

    parser = argparse.ArgumentParser(description='Data listener')
    parser.add_argument('-s', '--symbols', nargs='+',
                        help='List of companies to listen')
    parser.add_argument('-f', '--fake',  type=bool, default=False,
                        help='fake data for non-trading hours')
    args = parser.parse_args()
    passed_symbols = args.symbols
    loop = asyncio.get_event_loop()
    if args.fake:
        asyncio.ensure_future(fake_data_producer(passed_symbols), loop=loop)
    loop.run_until_complete(main(passed_symbols))

    # Wait 250 ms for the underlying SSL connections to close
    loop.run_until_complete(asyncio.sleep(0.250))
    loop.close()
