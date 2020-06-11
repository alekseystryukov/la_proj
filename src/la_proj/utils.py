from datetime import datetime
from bson import ObjectId
import json
import pytz


def json_serialize(obj):
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = pytz.utc.localize(obj).astimezone(pytz.utc)
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def json_dumps(*args, **kwargs):
    kwargs["default"] = json_serialize
    return json.dumps(*args, **kwargs)
