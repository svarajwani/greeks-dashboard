from fastapi import FastAPI
from contextlib import asynccontextmanager, suppress
import asyncio


from .tasks.poller import poll_loop
from .routers import ws

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(poll_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

app = FastAPI(lifespan=lifespan)
app.include_router(ws.router)