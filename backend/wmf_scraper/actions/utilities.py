from functools import wraps

from fastapi import HTTPException
from sqlmodel import Session


def exists_record(query, session: Session) -> bool:
    result = session.exec(query)
    return result.one_or_none() is not None


def try_endpoint(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as ex:
            raise HTTPException(status_code=400, detail=f"{ex}") from ex

    return wrapper


def optional_to_int_fallback_0(value: int | None) -> int:
    return value if value else 0
