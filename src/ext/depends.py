# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:49:15
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 18:47:04
# @Description: depends

from typing import Generator

from fastapi import Depends, Header, Query
from playhouse.pool import PooledPostgresqlExtDatabase

from src.ext.constant import Page
from src.ext.database import get_database
from src.ext.redis import get_client


def get_redis() -> Generator:
    """获取redis连接"""
    try:
        client = get_client()
        yield client
    finally:
        client.close()


async def reset_db_state() -> PooledPostgresqlExtDatabase:
    client = get_database()
    client._state._state.set(client.db_state_default.copy())
    client._state.reset()
    return client


def get_db(
    db_state: PooledPostgresqlExtDatabase = Depends(reset_db_state),
) -> Generator:
    try:
        db_state.connect()
        yield db_state
    finally:
        if not db_state.is_closed():
            db_state.close()


class HeaderInfo(object):
    """请求头信息"""

    def __init__(
        self,
        user_id: str = Header(..., alias="user-id", description="用户ID"),
        organization_id: str = Header(0, alias="organization-id", description="组织ID"),
        sub_organization_id: str = Header(
            "", alias="sub-organization-id", description="组织ID"
        ),
        request_id: str = Header(..., alias="request-id", description="请求ID"),
        is_ad: bool = Header(False, alias="is-ad", description="是否为AD用户"),
        company_id: str = Header("", alias="company-id", description="公司ID"),
        write: int = Header(0, alias="write", description="是否有写权限"),
    ):
        self.user_id = user_id
        self.organization_id = organization_id
        self.request_id = request_id
        self.is_ad = is_ad
        self.company_id = company_id
        self.sub_organization_id = sub_organization_id.split(",")
        self.write = write

    @staticmethod
    def keys():
        return (
            "user-id",
            "organization-id",
            "request-id",
            "write",
            "sub-organization-id",
            "is-ad",
            "company-id",
        )

    def keys_underline(self):
        return (
            "user_id",
            "organization_id",
            "request_id",
            "write",
            "sub_organization_id",
            "is_internal",
            "company_id",
        )

    def __getitem__(self, item):
        if item:
            print(f"item -- {item}")
            item = item.replace("-", "_")
            if item in self.keys_underline():
                return str(getattr(self, item))
            else:
                return None
        else:
            return None

    def __str__(self):
        return (
            f"user-id:{self.user_id},organization-id:{self.organization_id},"
            f"request-id:{self.request_id},write:{self.write},"
            f"sub-organization-id:{self.sub_organization_id},"
            f"is-ad:{self.is_ad},company-id:{self.company_id}"
        )

    def __repr__(self):
        return self.__str__()

    @property
    def class_to_dict(self):
        return {
            "user-id": self.user_id,
            "organization-id": self.organization_id,
            "request-id": self.request_id,
            "write": self.write,
            "sub-organization-id": self.sub_organization_id,
            "is-ad": self.is_ad,
            "company-id": self.company_id,
        }


class PageInfo(object):
    """分页信息"""

    def __init__(
        self,
        page_size: int = Query(5, alias="page_size", description="每页大小"),
        current: int = Query(1, alias="current", description=f"页码，-1获取所有"),
    ):
        self.page_size = (
            Page.MIN
            if page_size < Page.MIN
            else page_size
            if page_size < Page.MAX
            else Page.MAX
        )
        self.page_size = page_size
        self.current = -1 if current <= -1 else current

    def __str__(self):
        return f"page_size:{self.page_size},current:{self.current}"
