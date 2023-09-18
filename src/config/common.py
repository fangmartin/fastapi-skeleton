# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-12 18:19:08
# @Description: 公共配置
import enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class EnvEnum(str, enum.Enum):
    """环境枚举"""

    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Config(BaseSettings):
    ENV: EnvEnum = Field(EnvEnum.LOCAL, description="环境类型")

    CORS_ORIGINS: list[str] = Field(["*"], description="CORS origins")
    CORS_METHODS: list[str] = Field(["*"], description="CORS methods")
    CORS_HEADERS: list[str] = Field(["*"], description="CORS headers")
    CROS_CREDENTIALS: bool = Field(True, description="CORS allow credentials")

    LOGGER_CAPTURE: list[str]= Field([""], description="日志捕获")


@lru_cache
def get_settings() -> Config:
    return Config()


setting: Config = get_settings()
