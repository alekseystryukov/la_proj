from la_proj.settings import logger
from la_proj.storage import get_symbols, watch_changes_minute_stats, get_minute_stats
from la_proj.api.functions import DataProcessor
from la_proj.utils import json_dumps
from aiohttp import web, WSMsgType
import asyncio
import json


routes = web.RouteTableDef()


@routes.get("/api")
async def ping(request):
    return web.json_response({"text": "pong"}, status=200)


@routes.get("/api/symbols")
async def symbols(request):

    result = await get_symbols()
    return web.json_response(result, status=200)


# --- WebSockets ----
data_processor = DataProcessor()


class ChangesFeed:
    def __init__(self):
        self._symbols = {}
        asyncio.ensure_future(self._process_changes_loop())

    def subscribe(self, symbol, socket, queue):
        if symbol not in self._symbols:
            self._symbols[symbol] = {}
        self._symbols[symbol][socket] = queue

    def unsubscribe(self, symbol, socket):
        if symbol not in self._symbols:
            return logger.critical(f"Symbol {symbol} not in self._symbols")
        subscribers = self._symbols[symbol]
        subscribers.pop(socket)
        if not subscribers:
            logger.info(f"Empty subscribers set for {symbol}: discarding its cached object")
            del self._symbols[symbol]

    async def _process_changes_loop(self):
        logger.info(f"Start waiting for changes..")
        async for change in watch_changes_minute_stats():
            symbol = change.pop("symbol")
            data = [
                {
                    k: v
                    for k, v in change.items()
                    if k in ("open", "low", "high", "close", "volume", "time")
                }
            ]
            logger.info(f"Capture change of {symbol}")

            data_processor.calculate_functions(symbol, data)

            message = {"symbol": symbol, "data": data}
            if symbol in self._symbols:
                subscribers = self._symbols[symbol]
                dead_sockets = []
                for socket, subscriber in subscribers.items():
                    if subscriber.full():
                        dead_sockets.append(socket)
                    else:
                        subscriber.put_nowait(message)

                for socket in dead_sockets:
                    await socket.close()
                    logger.info('Force close of socket that is not reading data')
                    subscribers.pop(socket)


symbol_changes = ChangesFeed()


@routes.get('/api/changes_ws')
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info('Feed client connected. Waiting for symbols to subscribe')
    queue = asyncio.Queue(maxsize=20)
    functions = []  # functions to process data before sending to the recipient

    loop = asyncio.get_event_loop()
    t = loop.create_task(incoming_listener(ws, queue, functions))
    logger.info(f'Receive loop launched {t}')

    # get messages from the queue and send to client
    try:
        while not ws.closed:
            msg = await queue.get()
            # append function results
            for f in functions:
                msg[f] = data_processor.get_result(msg.get("symbol"), f)
            # send msg
            await ws.send_json(msg, dumps=json_dumps)
    except ConnectionResetError as e:
        logger.warning(f"ConnectionResetError at send updates {e}")
    logger.info('Feed client disconnected')
    return ws


async def incoming_listener(ws, queue, functions):
    subscribed_symbols = set()
    try:
        while not ws.closed:
            incoming = await ws.receive()
            logger.info("Got incoming msg", extra={"MESSAGE": incoming})
            if incoming.type is WSMsgType.TEXT:
                try:
                    data = json.loads(incoming.data)
                except ValueError as e:
                    logger.error(e)
                else:
                    new_functions = data.get("functions")
                    if new_functions:
                        # the same obj, but new contents
                        functions[:] = new_functions

                    subscribe = data.get("subscribe")
                    if subscribe:
                        subscribe = set(subscribe)
                        delete_symbols = subscribed_symbols - subscribe
                        for symbol in delete_symbols:
                            symbol_changes.unsubscribe(symbol, ws)

                        add_symbols = subscribe - subscribed_symbols
                        for symbol in add_symbols:
                            symbol_changes.subscribe(symbol, ws, queue)

                        logger.info(f"Subscribed to {add_symbols} and unsubscribed from {delete_symbols}")

                        for symbol in add_symbols:
                            start_data = await get_minute_stats(symbol)
                            queue.put_nowait(start_data)
    except ConnectionResetError as e:
        logger.warning(f"ConnectionResetError while getting data {e}")

    finally:
        logger.info(f"Unsubscribe socket from {subscribed_symbols}")
        for symbol in subscribed_symbols:
            symbol_changes.unsubscribe(symbol, ws)
