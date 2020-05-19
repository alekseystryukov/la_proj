from la_proj.settings import WS_ENDPOINT, WS_SESSION_HEADER
from la_proj.data.decoder import to_native
import aiohttp
import json


def process_message(msg):
    dict_msg = to_native(msg)


def main():
    session = aiohttp.ClientSession(headers=WS_SESSION_HEADER)
    ws = await session.ws_connect(WS_ENDPOINT)
    msg_data = {
        "subscribe": [
            "AAPL",
            #         "^FTSE","^FTMC","^FTAI","GBPEUR=X","GBPUSD=X","BTC-GBP","^CMC200","^GSPC",
            #         "^DJI","CL=F","GC=F","^N225","^HSI","^GDAXI","^FCHI"
        ]
    }
    await ws.send_str(json.dumps(msg_data))
    while True:
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.text:
            process_message(msg.data)
        elif msg.type == aiohttp.WSMsgType.closed:
            break
        elif msg.type == aiohttp.WSMsgType.error:
            break


if __name__ == "__main__":
    main()
