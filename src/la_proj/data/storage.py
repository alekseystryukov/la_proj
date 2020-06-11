from la_proj.settings import MONGODB_ERROR_INTERVAL, logger, MONGODB_MINUTE_COLLECTION
from la_proj.storage import get_mongodb_collection, get_minute_collection_name
from datetime import timedelta
from pymongo.errors import PyMongoError
import asyncio


MINUTE_COLLECTION = get_mongodb_collection(collection_name=MONGODB_MINUTE_COLLECTION)


async def update_minute_price(symbol, time, price, volume):
    # datetime(2020, 5, 18, 16, 55, 33) -> datetime(2020, 5, 18, 16, 56, 00)
    rounded_time = time.replace(second=0, microsecond=0)
    if rounded_time < time:  # pretty always
        rounded_time += timedelta(seconds=60)
    while True:
        try:
            return await MINUTE_COLLECTION.update_one(
                {
                    "symbol": symbol,
                    "time": rounded_time,
                },
                {
                    "$set": {"updated": time, "close": price, "volume": volume},
                    "$min": {"low": price},
                    "$max": {"high": price},
                    "$setOnInsert": {"open": price},

                    "$inc": {"updates": 1},
                },
                upsert=True
            )
        except PyMongoError as e:
            logger.error(f"Update stat exc {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
            await asyncio.sleep(MONGODB_ERROR_INTERVAL)
