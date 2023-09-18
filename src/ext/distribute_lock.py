# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:36:35
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-15 15:58:11
# @Description: 分布式锁

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Union

from redis import Redis, RedisCluster
from redis.exceptions import LockError, LockNotOwnedError
from redis.lock import Lock
from loguru import logger

pool = ThreadPoolExecutor(10)


class DistributeLock(Lock):
    """分布式锁，继承自`redis.asyncio.lock.Lock`，增加了WatchDog机制，防止锁过期后，业务还在执行"""

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
        self.stop_event:threading.Event = None

    @logger.catch
    def _watch(self) -> None:
        """循环执行续约"""
        logger.debug(f"分布式锁 {self.name}: 启动WatchDog")
        self.local.token = self.token
        event = self.stop_event
        while not event.is_set():
            logger.debug(f"分布式锁 {self.name}: 续约{self.timeout} s")
            try:
                self.extend(self.timeout)
            except LockNotOwnedError:
                logger.debug(f"分布式锁 {self.name}: 续约失败，锁已被释放")
                break
            time.sleep(self.timeout / 3)
        logger.debug(f"分布式锁 {self.name}: 关闭WatchDog")

    def _cancel_watch_dog(self):
        if self.stop_event and not self.stop_event.is_set():
            logger.debug(f"分布式锁 {self.name}: 通知关闭WatchDog")
            self.stop_event.set()

    def _new_watch_dog(self):
        logger.debug(f"分布式锁 {self.name}: 通知启动WatchDog")
        self.stop_event = threading.Event()
        pool.submit(self._watch)

    def acquire(
        self,
        blocking: Optional[bool] = None,
        blocking_timeout: Optional[float] = None,
        token: Optional[Union[str, bytes]] = None,
    ) -> bool:
        logger.info(f"{threading.get_ident()} lock")
        result = super().acquire(blocking, blocking_timeout, token)
        self.token = self.local.token  # 新的线程中，不会拷贝local
        if result:  # 取消正在运行的WatchDog协程,并启动新的WatchDog协程
            self._cancel_watch_dog()
            self._new_watch_dog()
        return result

    def release(self) -> None:
        """释放锁：取消WatchDog，再调用父类的释放锁方法，释放失败，则由超时机制兜底"""
        logger.debug(f"分布式锁 {self.name}: 释放")
        super().release()
        self._cancel_watch_dog()

    def __enter__(self) -> "Lock":
        if self.acquire():
            return self
        raise LockError("加锁失败")

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()

    def __del__(self) -> None:
        try:
            self._cancel_watch_dog()
        except Exception:
            pass
