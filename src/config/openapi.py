# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-12 18:05:38
# @Description: 公共配置
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    OPEN_DOC: bool = Field(True, description="是否开启文档")
    DOC_TITLE: str = Field("FastAPI Skeleton", description="文档标题")

@lru_cache
def get_settings() -> Config:
    return Config()


setting: Config = get_settings()
