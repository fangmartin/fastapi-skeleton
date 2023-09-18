# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 18:48:10
# @Description: redis 客户端

from functools import lru_cache

import redis

from src.config.redis import setting


async def get_async_client() -> redis.asyncio.Redis:
    pool = redis.asyncio.ConnectionPool.from_url(
        str(setting.REDIS_URL), 
        encoding="utf8",
        max_connections=setting.REDIS_POOL_SIZE
        )
    client = redis.asyncio.Redis(connection_pool=pool)
    client.initialize()
    await client.ping()
    return client


@lru_cache
def get_client() -> redis.Redis:
    pool = redis.ConnectionPool.from_url(
        str(setting.REDIS_URL), 
        encoding="utf8",
        max_connections=setting.REDIS_POOL_SIZE
        )
    client = redis.Redis(connection_pool=pool)
    client.ping()
    return client