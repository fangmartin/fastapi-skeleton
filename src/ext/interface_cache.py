# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 17:35:52
# @Description: 接口缓存

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from src.ext.redis import get_async_client


async def init_cache():
    client = await get_async_client()
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")


cache = cache
