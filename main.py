# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-04 10:18:33
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 17:28:05
# @Description:

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config.common import setting
from src.ext.exceptions import init_exception_handler
from src.ext.interface_cache import init_cache
from src.ext.logging import init_log
from src.ext.redis import get_client as get_redis_client
from src.openapi import openapi
from src.tasks.scheduler import scheduler

init_log()


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    """生命周期管理"""
    # Startup
    redis_client = await get_redis_client()

    scheduler.start()
    await init_cache()

    yield
    # Shutdown
    scheduler.shutdown()
    await redis_client.close()



app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

app.include_router(openapi.router)  # 注册openapi路由

app.add_middleware(  # 注册跨域中间件
    CORSMiddleware,
    allow_origins=setting.CORS_ORIGINS,
    allow_credentials=setting.CROS_CREDENTIALS,
    allow_methods=setting.CORS_METHODS,
    allow_headers=setting.CORS_HEADERS,
)
init_log()  # 初始化日志
init_exception_handler(app) # 初始化异常处理


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
