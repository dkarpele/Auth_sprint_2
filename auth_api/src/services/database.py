from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis import Redis, get_redis, AbstractCache
from db.postgres import get_session


@lru_cache()
def get_cache_service(
        redis: Redis = Depends(get_redis)) -> AbstractCache:
    return redis


@lru_cache()
def get_db_service(
        db: AsyncSession = Depends(get_session)) -> AsyncSession:
    return db


DbDep = Annotated[AsyncSession, Depends(get_db_service)]
CacheDep = Annotated[AbstractCache, Depends(get_cache_service)]
