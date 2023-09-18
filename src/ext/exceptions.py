# -*- coding: utf-8 -*-
# @Author: martin fangjie.martin@gmail.com
# @Date: 2023-09-04 00:10:00
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-13 18:30:54
# @Description: 公共异常
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException as FastapiHTTPException
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pydantic.errors import *
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.ext.response import APIResponse


class DetailedHTTPException(FastapiHTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"
    HEADERS = {}

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(
            status_code=self.STATUS_CODE,
            detail=self.DETAIL,
            headers=self.HEADERS,
            **kwargs,
        )


class PermissionDenied(DetailedHTTPException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denied"


class NotFound(DetailedHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND


class BadRequest(DetailedHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad Request"


class NotAuthenticated(DetailedHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> APIResponse:
    """参数校验错误处理"""
    return APIResponse(
        http_status_code=status.HTTP_400_BAD_REQUEST,
        api_code=-1,
        message=f"参数校验错误:{exc.errors()}",
    )


async def all_exception_handler(_: Request, exc: Exception) -> APIResponse:
    """所有异常的错误拦截处理"""
    if isinstance(exc, StarletteHTTPException) or isinstance(exc, FastapiHTTPException):
        return APIResponse(
            http_status_code=exc.status_code,
            api_code=-1,
            message=exc.detail,
        )
    else:
        # 其他内部的异常的错误拦截处理
        logger.exception(exc)
        return APIResponse(
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            api_code=-1,
            message="内部异常",
        )


async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> APIResponse:
    """http错误处理"""
    return APIResponse(
        http_status_code=exc.status_code,
        api_code=-1,
        message=exc.detail,
    )


def init_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(Exception, handler=all_exception_handler)
    # 捕获StarletteHTTPException返回的错误异常，如返回405的异常的时候，走的是这个地方
    app.add_exception_handler(StarletteHTTPException, handler=http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, handler=validation_exception_handler
    )
