from la_proj.settings import logger
from aiohttp import web
import asyncio


routes = web.RouteTableDef()


@routes.get('/api')
async def ping(request):
    return json_response({'text': 'pong'}, status=200)


# --- WebSockets ----

class ChangesFeed:
    def __init__(self):
        self._auctions = {}
        asyncio.ensure_future(self._process_changes_loop())

    def get(self, key):
        auction_doc = self._auctions.get(key, {}).get("doc")
        return auction_doc

    def subscribe(self, auction_id, socket):
        if auction_id not in self._auctions:
            subscribers = {}
            self._auctions[auction_id] = dict(doc=None, subscribers=subscribers)
        else:
            subscribers = self._auctions[auction_id]["subscribers"]

        queue = asyncio.Queue(maxsize=10)
        subscribers[socket] = queue
        return queue

    def unsubscribe(self, auction_id, socket):
        if auction_id not in self._auctions:
            return logger.critical(f"Auction id {auction_id} not in self._auctions")

        subscribers = self._auctions[auction_id]["subscribers"]
        subscribers.pop(socket)

        if not subscribers:
            logger.info(f"Empty subscribers set for {auction_id}: discarding its cached object")
            del self._auctions[auction_id]

    async def _process_changes_loop(self):

        async for auction in watch_changed_docs():
            auction_id = auction["_id"]
            logger.info(f"Capture change of {auction_id}")

            if auction_id in self._auctions:
                save_doc = self._auctions[auction_id]["doc"]
                if save_doc is None or save_doc["modified"] != auction["modified"]:
                    self._auctions[auction_id]["doc"] = auction
                    subscribers = self._auctions[auction_id]["subscribers"]
                    dead_sockets = []
                    for socket, subscriber in subscribers.items():
                        if subscriber.full():
                            dead_sockets.append(socket)
                            continue
                        subscriber.put_nowait(1)  # putting any object is fine

                    for socket in dead_sockets:
                        await socket.close()
                        logger.info('Force close of socket that is not reading data')
                        subscribers.pop(socket)


AUCTION_FEED = ChangesFeed()


def get_auction_feed():
    global AUCTION_FEED
    AUCTION_FEED = AUCTION_FEED or ChangesFeed()
    return AUCTION_FEED


async def ping_ws(ws):
    try:
        while not ws.closed:
            await asyncio.sleep(5)
            await ws.send_str("PING")  # send it, so client is sure that connection is fine
            res = await ws.receive(timeout=5)  # we do actually nothing if there is no pong
            logger.debug(f"Ping response: {res.data}")
    except ConnectionResetError as e:
        logger.warning(f"ConnectionResetError at ping {e}")


@routes.get('/api/changes_ws')
async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    auction_id = request.match_info['auction_id']
    log_extra = {"auction_id": auction_id}
    logger.info('Feed client connected', extra=log_extra)

    loop = asyncio.get_event_loop()
    t = loop.create_task(ping_ws(ws))
    logger.info(f'Ping launched {t}', extra=log_extra)

    auction_feed = get_auction_feed()
    feed = auction_feed.subscribe(auction_id, ws)
    try:
        while not ws.closed:
            await feed.get()  # will get 1 from _process_changes_loop
            await ws.send_json(auction_feed.get(auction_id), dumps=json_dumps)
    except ConnectionResetError as e:
        logger.warning(f"ConnectionResetError at send updates {e}")
    finally:
        logger.info("Unsubscribe socket")
        auction_feed.unsubscribe(auction_id, ws)

    logger.info('Feed client disconnected')
    return ws
