from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from slr_app.routers import activity, begin, feature_extraction, recognize, rating
from hse_slr.models.utils import SLInference


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.inference_thread = SLInference(recognize.CONFIG_PATH)
    redis = aioredis.from_url("redis://redis", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    del app.state.inference_thread

app = FastAPI(
    debug=True,
    title='SignLingoDetectorApp',
    summary='FastAPI app to detect russian sign language from video.',
    version='0.1.0',
    lifespan=lifespan
)

app.include_router(begin.router)
app.include_router(activity.router)
app.include_router(feature_extraction.router)
app.include_router(recognize.router)
app.include_router(rating.router)
