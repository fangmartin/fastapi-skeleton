# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-13 16:08:25
# @Description: redis 客户端

import redis

from src.config.redis import setting


async def get_client() -> redis.asyncio.Redis:
    pool = redis.asyncio.ConnectionPool.from_url(
        str(setting.REDIS_URL), 
        encoding="utf8",
        max_connections=setting.REDIS_POOL_SIZE
        )
    client = redis.asyncio.Redis(connection_pool=pool)
    await client.ping()
    return client
