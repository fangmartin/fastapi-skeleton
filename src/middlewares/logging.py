# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-05 14:15:57
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-13 15:42:37
# @Description: 提供日志中间件

import logging
import sys
import uuid

from loguru import logger
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.config.common import EnvEnum, setting
from src.ext.logging import TraceID


def _log_filter(record: dict):
    """日志过滤器"""
    record["trace_msg"] = f"{TraceID.get_request_id()} | {TraceID.get_trace_id()}"
    return record["trace_msg"]


class LoguruLoggerWithRequestIDMiddleware(BaseHTTPMiddleware):
    """Loguru logger middleware with request id."""

    def __init__(
        self, app: ASGIApp, header: str = "X-Request-ID", level=logging.DEBUG
    ) -> None:
        """
        :param app: ASGI app
        :param header: request header name
        :param level: log level
        """
        super().__init__(app)
        logger.remove()  # 移除默认的logger

        self.header = header

        # 配置logger输出格式
        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "level": "INFO" if setting.ENV is EnvEnum.PROD else "DEBUG",
                    "encoding": "utf-8",
                    "enqueue": True,  # 开启异步
                    "backtrace": True
                    if setting.ENV != EnvEnum.PROD
                    else False,  # 开启错误追踪
                    "filter": _log_filter,
                    "format": (
                        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {trace_msg} | "
                        "{name}:{function}:{line} - {message}"
                    ),
                }
            ]
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(self.header, uuid.uuid4())
        TraceID.set_request_id(request_id)
        request.state.request_id = request_id
        return await call_next(request)
