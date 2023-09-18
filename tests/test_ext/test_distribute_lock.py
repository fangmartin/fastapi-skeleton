# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:49:15
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-18 17:21:02
# @Description: 分布式锁测试
import time

from src.ext.distribute_lock import DistributeLock
from src.ext.redis import get_client


def test_distribute_lock():
    client = get_client()
    with DistributeLock(client, "test", timeout=1):
        time.sleep(5)
        assert client.get("test") is not None
