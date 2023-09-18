# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:36:35
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 18:17:52
# @Description: 分布式锁

import asyncio
from typing import Optional, Union

from redis.asyncio import Redis, RedisCluster
from redis.asyncio.lock import Lock
from redis.exceptions import LockError


class DistributeLock(Lock):
    """分布式锁，继承自`redis.asyncio.lock.Lock`，增加了WatchDog机制，防止锁过期后，业务还在执行"""

    _watch_dog: Optional[asyncio.Task]

    def __init__(
        self,
        redis: Union["Redis", "RedisCluster"],
        name: Union[str, bytes, memoryview],
        timeout: Optional[float] = None,
        sleep: float = 0.1,
        blocking: bool = True,
        blocking_timeout: Optional[float] = None,
        thread_local: bool = True,
    ):
        """
        创建一个新的分布式锁实例，
        redis：Redis客户端
        name：锁的名称
        timeout：锁的过期时间，单位秒，默认不过期，直到调用release()方法
        sleep：获取锁失败后，每次重试的间隔时间
        blocking：是否阻塞获取锁，如果为False，则获取失败后立即返回
        blocking_timeout：阻塞获取锁的超时时间，单位秒
        thread_local：是否将锁的token存储在线程本地存储中，
            避免其他线程释放锁(如果设置了timeout，默认情况下，锁会在timeout秒后自动释放，
            其他线程可能会获取到锁。当第一个线程执行完任务后，可能会释放第二个线程的锁)。
            如果为False，则所有线程共享一个token
        """
        super().__init__(
            redis, name, timeout, sleep, blocking, blocking_timeout, thread_local
        )
        self._watch_dog = None

    async def _watch(self) -> None:
        """循环执行续约"""
        while True:
            await self.extend(self.timeout)
            await asyncio.sleep(self.timeout / 3)

    def _cancel_watch_dog(self) -> None:
        """取消正在运行的WatchDog协程"""
        _old_watch_dog: Optional[asyncio.Future] = getattr(self, "_watch_dog", None)
        if _old_watch_dog and not _old_watch_dog.cancelled():
            _old_watch_dog.cancel()

    async def acquire(
        self,
        blocking: Optional[bool] = None,
        blocking_timeout: Optional[float] = None,
        token: Optional[Union[str, bytes]] = None,
    ) -> bool:
        result = await super().acquire(blocking, blocking_timeout, token)
        if result:
            # 启动WatchDog机制：取消旧的WatchDog，再通过`asyncio.create_task`执行WatchDog
            self._cancel_watch_dog()
            self._watch_dog = asyncio.create_task(self._watch())
        return result

    async def do_release(self, expected_token: bytes) -> None:
        """释放锁：取消WatchDog，再调用父类的释放锁方法，释放失败，则由超时机制兜底"""
        self._cancel_watch_dog()
        return await super().do_release(expected_token)

    async def __aenter__(self) -> "Lock":
        if await self.acquire():
            return self
        raise LockError("Unable to acquire lock within the time specified")

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.do_release()

    def __del__(self) -> None:
        try:
            self._cancel_watch_dog()
        except Exception:
            pass
