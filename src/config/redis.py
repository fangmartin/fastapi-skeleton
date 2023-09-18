# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-11 18:27:41
# @Description: redis配置

from functools import lru_cache

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    REDIS_URL: RedisDsn
    REDIS_POOL_SIZE: int = Field(10, description="redis连接池大小")


@lru_cache
def get_settings() -> Config:
    return Config()


setting: Config = get_settings()