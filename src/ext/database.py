# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:36:35
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-13 18:22:08
# @Description: 数据库
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config.database import setting


class Base(AsyncAttrs, DeclarativeBase):
    pass


async_engine = create_async_engine(
    str(setting.PG_URL),
    echo=setting.PG_ECHO,
    future=True,  # 使用 SQLAlchemy 2.0 API，向后兼容
    pool_size=setting.PG_POOL_SIZE,
    pool_recycle=setting.PG_RECYCLE,
)

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

__db_session: ContextVar[AsyncSession] = ContextVar("db_session")


def get_session() -> AsyncSession:
    s = __db_session.get()
    if not s:
        s = AsyncSessionLocal()
        __db_session.set(s)
    return s
