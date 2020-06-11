from motor.motor_asyncio import AsyncIOMotorClient
from la_proj.settings import (
    MONGODB_ERROR_INTERVAL,
    MONGODB_COLLECTION, MONGODB_URL,
    MONGODB_DATABASE, MONGODB_WRITE_CONCERN,
    MONGODB_MINUTE_COLLECTION,
    logger,
)
from pymongo.errors import PyMongoError
from aiohttp import web
import asyncio
import re

DB_CONNECTION = None


def get_mongodb_collection(collection_name=MONGODB_MINUTE_COLLECTION):
    global DB_CONNECTION
    DB_CONNECTION = DB_CONNECTION or AsyncIOMotorClient(MONGODB_URL, w=MONGODB_WRITE_CONCERN)
    db = getattr(DB_CONNECTION, MONGODB_DATABASE)
    collection = getattr(db, collection_name)
    return collection


def get_minute_collection_name(symbol):
    symbol_code = re.sub(r"\W", "_", symbol)
    return f"{MONGODB_MINUTE_COLLECTION}_{symbol_code}"


async def get_symbols(offset=0, limit=3000):
    collection = get_mongodb_collection(collection_name=MONGODB_COLLECTION)
    result = []
    query = {}
    try:
        cursor = collection.find(
            query,
            {"name": 1}
        )
        async for obj in cursor.skip(offset).limit(limit):
            result.append(dict(id=obj["_id"], name=obj["name"]))
    except PyMongoError as e:
        logger.error(f"Mongodb error {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
        raise web.HTTPInternalServerError()
    else:
        return result


async def watch_changes_minute_stats():
    collection = get_mongodb_collection(collection_name=MONGODB_MINUTE_COLLECTION)
    resume_after = None
    while True:
        logger.info(f"Start watching mongodb changes after {resume_after}")
        changes = collection.watch(full_document="updateLookup", resume_after=resume_after)
        while True:
            try:
                change = await changes.next()
            except PyMongoError as e:
                logger.error(f"Got feed error {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
                await asyncio.sleep(MONGODB_ERROR_INTERVAL)
            except StopAsyncIteration as e:
                logger.exception(e)
                resume_after = None
                break
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(MONGODB_ERROR_INTERVAL)
            else:
                resume_after = change["_id"]
                if "fullDocument" in change:   # present in insert/update changes
                    yield change["fullDocument"]


async def get_minute_stats(symbol, limit=3000):
    collection = get_mongodb_collection(collection_name=MONGODB_MINUTE_COLLECTION)
    result = []
    try:
        cursor = collection.find(
            {"symbol": symbol},
        )
        async for obj in cursor.limit(limit):
            obj["id"] = str(obj.pop("_id"))
            del obj["symbol"]
            result.append(obj)
    except PyMongoError as e:
        logger.error(f"Mongodb error {type(e)}: {e}", extra={"MESSAGE_ID": "MONGODB_EXC"})
        raise web.HTTPInternalServerError()
    else:
        return {"symbol": symbol, "data": result}
