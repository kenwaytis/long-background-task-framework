from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.v1.websocket_endpoint import router
from dependencies import get_task_manager

app = FastAPI()

app.include_router(router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    task_manager = get_task_manager()
    task_manager.shutdown()