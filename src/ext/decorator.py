# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-11 18:36:35
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-11 18:37:26
# @Description: 装饰器

from datetime import datetime
from functools import wraps

from loguru import logger


def log_use_time(func):
    """记录函数执行耗时"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        logger.info(f"execute used time {(datetime.now() - start_time).total_seconds()} s")
        return result

    return wrapper