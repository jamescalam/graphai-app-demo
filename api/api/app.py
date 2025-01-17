import asyncio
from contextlib import asynccontextmanager

from dotenv import find_dotenv, load_dotenv
from fastapi import APIRouter, Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from starlette.responses import StreamingResponse

from .agent import create_graph
from .schemas import Interaction


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

router = APIRouter()

ALLOW_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = create_graph()


async def gen(callback):
    async for token in callback.aiter():
        yield token


@router.post("/chat", tags=["Chat"])
async def chat(request: Request, msg: Interaction = Body(...)):
    # grab a new callback object
    callback = graph.get_callback()

    response_generator = asyncio.create_task(
        graph.execute(
            input={"input": {
                "query": msg.message,
                "chat_history": msg.chat_history
            }}
        )
    )
    return StreamingResponse(
        gen(callback), media_type="text/plain"
    )

app.include_router(router)