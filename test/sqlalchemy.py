# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-12 15:44:58
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 18:24:11
# @Description:

import asyncio
import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class B(Base):
    __tablename__ = "b"
    id: Mapped[int] = mapped_column(primary_key=True)
    a_id: Mapped[int]
    data: Mapped[str] = mapped_column(server_default="b data", nullable=True)


class A(Base):
    __tablename__ = "a"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[str]
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            a1 = A(data="a1")
            a2 = A(data="a2")
            session.add_all([a1, a2])
            await session.flush()
            b1 = B(a_id=a1.id, data="b1")
            b2 = B(a_id=a2.id, data="b2")
            session.add_all([b1, b2])
            await session.flush()


async def select_and_update_objects(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    async with async_session() as session, session.begin():
        conditions = [A.data.in_(["a1", "a2"]), A.id==1]
        stmt = select(A, B).join(
            B, A.id == B.a_id, isouter=True
        ).where(*conditions)

        result = await session.execute(stmt)
        a: A
        b: B
        for a,b in result.all():
            print(a,b)
            print(f"created at: {a.create_date}")

        result = await session.execute(stmt)
        for a,b in result:
            print(a,b)
            print(f"created at: {a.create_date}")

        result = await session.execute(stmt)
        for a in result.scalars():
            print(a)
            print(f"created at: {a.create_date}")

        # result = await session.execute(select(A).order_by(A.id).limit(1))

        # a1 = result.scalars().one()

        # a1.data = "new data"

        # await session.commit()

        # # access attribute subsequent to commit; this is what
        # # expire_on_commit=False allows
        # print(a1.data)

        # # alternatively, AsyncAttrs may be used to access any attribute
        # # as an awaitable (new in 2.0.13)
        # for b1 in await a1.awaitable_attrs.bs:
        #     print(b1)


async def async_main() -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:vastai@10.23.4.247:5432/test",
        echo=True,  # echo 设为 True 会打印出实际执行的 sql，调试的时候更方便
        future=True,  # 使用 SQLAlchemy 2.0 API，向后兼容
        pool_size=5,  # 连接池的大小默认为 5 个，设置为 0 时表示连接无限制
        pool_recycle=3600,  # 设置时间以限制数据库自动断开
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await insert_objects(async_session)
    await select_and_update_objects(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


asyncio.run(async_main())
