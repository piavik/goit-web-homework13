import uvicorn
import redis.asyncio as redis

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from src.routes import routes, auth
from src.config.settings import settings

app = FastAPI()

app.include_router(routes.router, prefix='/api')
app.include_router(auth.router, prefix='/auth')

cors_origins = [ 
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup() -> None:
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root() -> dict:
    return {"message": "GoIT homework #11-13 - REST API via FastAPI"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
