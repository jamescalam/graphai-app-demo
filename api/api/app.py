from contextlib import asynccontextmanager

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.redis = Redis(host="redis", port=6379)

        # Configure Redis to use LFU eviction and 100mb memory limit
        # When memory is full, least frequently used items will be removed
        # See https://redis.io/docs/latest/develop/reference/eviction/#eviction-policies for more info
        await app.state.redis.config_set("maxmemory-policy", "allkeys-lfu")
        await app.state.redis.config_set("maxmemory", "100mb")
        # redis_info = await app.state.redis.info()
        # logger.info(f"Redis info: {redis_info}")

        yield
    finally:
        # list pending tasks
        # pending = asyncio.all_tasks()
        # for task in pending:
        #     logger.info(task)
        await app.state.redis.close()

load_dotenv(find_dotenv())

app = FastAPI(lifespan=lifespan)

ALLOW_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
