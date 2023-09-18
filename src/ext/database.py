# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:36:35
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 18:47:29
# @Description: 数据库
from contextvars import ContextVar
from functools import lru_cache

from peewee import _ConnectionState
from playhouse.pool import PooledPostgresqlExtDatabase

from src.config.database import setting


@lru_cache
def get_database() -> PooledPostgresqlExtDatabase:
    """获取数据库连接"""
    db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
    db_state = ContextVar("db_state", default=db_state_default.copy())

    # 使用contextvars，将数据库连接状态保存在上下文中，避免多线程下，数据库连接状态混乱
    class PeeweeConnectionState(_ConnectionState):
        def __init__(self, **kwargs):
            super().__setattr__("_state", db_state)
            super().__init__(**kwargs)

        def __setattr__(self, name, value):
            self._state.get()[name] = value

        def __getattr__(self, name):
            return self._state.get()[name]

    _database = PooledPostgresqlExtDatabase(
        setting.PG_URL,
        max_connections=setting.PG_MAX_CONNECTIONS,  # 最大连接数
        # stale_timeout：配置连接池中，连接的生命周期。当超过stale_timeout，则不再被分配。只有当需要创建新连接时，才会回收
        stale_timeout=setting.PG_STALE_TIMEOUT,
        timeout=setting.PG_TIME_OUT,
    )
    _database._state = PeeweeConnectionState()
    _database.db_state_default = db_state_default
    return _database
