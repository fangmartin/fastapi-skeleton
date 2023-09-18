# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-08 17:48:10
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-11 17:57:17
# @Description: 接口频率限制

import inspect
from functools import wraps
from typing import (Awaitable, Callable, List, Optional, ParamSpec, TypeVar,
                    Union)

from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.wrappers import Limit, LimitGroup
from starlette.responses import Response

P = ParamSpec("P")
R = TypeVar("R")


def _get_ipaddr(request: Request) -> str:
    if "x-forwarded-for" in request.headers:
        addr = request.headers["x-forwarded-for"]  # 小写的
    else:
        if not request.client or not request.client.host:
            return "127.0.0.1"

        addr = request.client.host
    return addr


_limiter = Limiter(key_func=_get_ipaddr)


def http_limit(
    limit_value: Union[str, Callable[[str], str]],
    key_func: Optional[Callable[..., str]] = None,
    per_method: bool = False,
    methods: Optional[List[str]] = None,
    error_message: Optional[str] = None,
    exempt_when: Optional[Callable[..., bool]] = None,
    cost: Union[int, Callable[..., int]] = 1,
    override_defaults: bool = True,
):
    """
    限制HTTP路由函数的访问频率
    * **limit_value**: 限制速率字符串(1/second,1/minute,1/hour)或返回字符串的函数(动态)
    * **key_func**: 提取请求的唯一标识符
    * **per_method**: 是否为每个HTTP方法单独限制
    * **methods**: 限制指定http请求方法
    * **error_message**: 超过限制时返回的错误信息
    * **exempt_when**: 豁免函数，返回True时不限制
    * **cost**: 每次请求的消耗
    * **override_defaults**: 是否覆盖默认配置
    """
    def wrapper(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        """为路由函数注入request和response参数"""
        signature = inspect.signature(func)
        request_param = next(
            (param for param in signature.parameters.values() if param.annotation is Request),
            None,
        )
        response_param = next(
            (param for param in signature.parameters.values() if param.annotation is Response),
            None,
        )
        parameters = []
        extra_params = []
        for p in signature.parameters.values():
            if p.kind <= inspect.Parameter.KEYWORD_ONLY:
                parameters.append(p)
            else:
                extra_params.append(p)
        if not request_param:
            parameters.append(
                inspect.Parameter(
                    name="request",
                    annotation=Request,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                ),
            )
        if not response_param:
            parameters.append(
                inspect.Parameter(
                    name="response",
                    annotation=Response,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                ),
            )
        parameters.extend(extra_params)
        if parameters:
            signature = signature.replace(parameters=parameters)
        func.__signature__ = signature

        _scope = None

        keyfunc = key_func or _limiter._key_func
        name = f"{func.__module__}.{func.__name__}"
        dynamic_limit = None
        static_limits: List[Limit] = []
        if callable(limit_value):
            dynamic_limit = LimitGroup(
                limit_value,
                keyfunc,
                _scope,
                per_method,
                methods,
                error_message,
                exempt_when,
                cost,
                override_defaults,
            )
        else:
            try:
                static_limits = list(
                    LimitGroup(
                        limit_value,
                        keyfunc,
                        _scope,
                        per_method,
                        methods,
                        error_message,
                        exempt_when,
                        cost,
                        override_defaults,
                    )
                )
            except ValueError as e:
                _limiter.logger.error(
                    "Failed to configure throttling for %s (%s)",
                    name,
                    e,
                )
        _limiter._Limiter__marked_for_limiting.setdefault(name, []).append(func)
        if dynamic_limit:
            _limiter._dynamic_route_limits.setdefault(name, []).append(dynamic_limit)
        else:
            _limiter._route_limits.setdefault(name, []).extend(static_limits)

        @wraps(func)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            async def ensure_async_func(*args: P.args, **kwargs: P.kwargs) -> R:
                """Run cached sync functions in thread pool just like FastAPI."""
                # if the wrapped function does NOT have request or response in its function signature,
                # make sure we don't pass them in as keyword arguments
                if not request_param:
                    kwargs.pop("request", None)
                if not response_param:
                    kwargs.pop("response", None)

                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return await run_in_threadpool(func, *args, **kwargs)
                
            if _limiter.enabled:
                copy_kwargs = kwargs.copy()
                request: Optional[Request] = copy_kwargs.pop("request", None)
                    
                if not isinstance(request, Request):
                    raise Exception(
                        "parameter `request` must be an instance of starlette.requests.Request"
                    )

                if _limiter._auto_check and not getattr(
                    request.state, "_rate_limiting_complete", False
                ):
                    _limiter._check_request_limit(request, func, False)
                    request.state._rate_limiting_complete = True

            response = await ensure_async_func(*args, **kwargs)
            
            if _limiter.enabled:
                if not isinstance(response, Response):
                    # get the response object from the decorated endpoint function
                    _limiter._inject_headers(
                        kwargs.get("response"), request.state.view_rate_limit  # type: ignore
                    )
                else:
                    _limiter._inject_headers(
                        response, request.state.view_rate_limit
                    )
            return response
        
        return inner
    
    return wrapper