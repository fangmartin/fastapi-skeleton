# 简介

参考Netflix的[dispatch](https://github.com/Netflix/dispatch/blob/master/README.md)项目的Python FastAPI项目框架。

## 配置参数

### 文档

- OPEN_DOC: 是否开放文档，默认为`True`
- TITLE：文档标题，默认为`FastAPI Skeleton`

## 设计准则
设计准则参考：[fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)
1. 目录结构简单，通过名称即可了解模块功能
2. 善用Pydantic
   1. 校验输入合法性
   2. 应用配置读取
3. 善用Depends
   1. 基于数据库验证数据
   2. Depends嵌套，避免代码重复
   3. FastAPI默认在请求的scope中缓存Depends的结果，因此推荐将Depends解耦到作用域很小的函数中，便于重用
4. 路由设计遵循REST风格
5. 异步路由中不要使用阻塞I/O操作
6. 文档管理
   1. 除非API是对外公开，否则默认隐藏文档
   2. 通过`response_model`、`status_code`、`description`等属性协助FastAPI生成更容易理解的文档