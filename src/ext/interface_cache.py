# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martin martin@vastaitech.com
# @LastEditTime: 2023-09-18 17:24:24
# @Description: 接口缓存

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from src.ext.redis import get_client


async def init_cache():
    client = await get_client()
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")


cache = cache
