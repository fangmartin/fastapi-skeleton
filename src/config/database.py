# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-12 18:00:00
# @Description: 数据库配置
from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PG_URL: PostgresDsn
    PG_POOL_SIZE: int = Field(10, description="连接池的大小默认为 10 个，设置为 0 时表示连接无限制")
    PG_RECYCLE: int = Field(3600, description="设置时间以限制数据库自动断开")
    PG_ECHO: bool = Field(True, description="是否打印sql")


@lru_cache
def get_settings() -> Config:
    return Config()


setting: Config = get_settings()
