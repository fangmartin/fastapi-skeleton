# -*- coding: utf-8 -*-
# @Author: martinf fangjie.martin@gmail.com
# @Date: 2023-09-13 17:09:08
# @LastEditors: martinf fangjie.martin@gmail.com
# @LastEditTime: 2023-09-14 17:38:56
# @Description:

import typing

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    code: int = Field(0, description="错误码")
    message: str = Field("成功", description="描述信息")
    data: typing.Any = Field(description="数据")


class APIResponse(JSONResponse):
    def __init__(self, status_code: int, api_code: int, message: str,  data: str | dict = None):
        super(APIResponse,self).__init__(
            {"code": api_code, "message": message, "data": data}, status_code=status_code
        )
