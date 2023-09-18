# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-04 10:18:33
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-12 18:05:27
# @Description: OPENAPI 文档管理
from fastapi import APIRouter, Request

from src.config.openapi import setting

router = APIRouter()

if setting.OPEN_DOC:
    from pathlib import Path

    from fastapi.openapi.docs import get_swagger_ui_html
    from fastapi.staticfiles import StaticFiles

    local_file = Path(__file__)

    file = StaticFiles(directory=local_file.parent / "swagger")

    @router.get("/static/{name:str}", include_in_schema=False)
    async def static(request: Request, name: str):
        return await file.get_response(name, request.scope)

    @router.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=setting.DOC_TITLE + " - Swagger UI",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )
