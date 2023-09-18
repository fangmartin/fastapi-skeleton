import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from src.ext.rate_limiter import http_limit
app = FastAPI()



@app.get("/")
@cache(expire=60)
@http_limit("1/second")
async def index(request:Request):
    print(11)
    return dict(hello="world")


@app.on_event("startup")
async def startup():
    pool = redis.ConnectionPool.from_url("redis://:vastai@10.23.4.247:31379/0", encoding="utf8")
    client = redis.Redis(connection_pool=pool)
    # redis = await redis.R.("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)