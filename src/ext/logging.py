# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-05 14:15:57
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-13 16:03:12
# @Description: 提供日志中间件

import logging
import uuid
from contextvars import ContextVar

from loguru import logger

from src.config.common import EnvEnum, setting

_x_trace_id: ContextVar[str] = ContextVar("x_trace_id", default="")  # 追踪子任务
_x_request_id: ContextVar[str] = ContextVar("x_request_id", default="")  # 追踪请求


class TraceID:
    @staticmethod
    def get_trace_id() -> str:
        """获取trace_id"""
        return _x_trace_id.get()

    @staticmethod
    def get_request_id() -> str:
        """获取trace_id"""
        return _x_request_id.get()
    
    @staticmethod
    def set_trace_id(trace_id: str) -> ContextVar[str]:
        """设置trace_id"""
        trace_id = trace_id or uuid.uuid4().hex()
        return _x_trace_id.set(trace_id)

    @staticmethod
    def set_request_id(request_id: str) -> ContextVar[str]:
        """设置request_id"""
        request_id = request_id or uuid.uuid4().hex()
        return _x_request_id.set(request_id)


class InterceptHandler(logging.Handler):
    """将logging的日志转换为loguru的日志"""

    def emit(self, record):
        try:  # 获取真实日志级别
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 从当前栈帧开始追溯，直到找到第一个不是logging模块的栈帧
        # 2表示默认向上回溯两层，即当前代码所在的函数或方法的调用者栈帧
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        # 调用loguru，记录日志信息
        logger.opt(depth=(depth + 1), exception=record.exc_info).log(
            level, record.getMessage()
        )


def init_log() -> None:
    # 拦截所有日志输出
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO if setting.ENV == EnvEnum.PROD else logging.DEBUG)

    # 移除相关的logger的handlers，使其使用root logger的handlers
    for name in logging.root.manager.loggerDict.keys():
        for c in setting.LOGGER_CAPTURE:
            if name.startswith(c):
                logging.getLogger(name).handlers = []  # 将handlers设置为空列表
                logging.getLogger(name).propagate = True  # 向父logger传递日志
