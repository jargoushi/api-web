from datetime import datetime

from fastapi.encoders import jsonable_encoder as default_jsonable_encoder


def custom_jsonable_encoder(obj, **kwargs):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    return default_jsonable_encoder(obj, **kwargs)
