import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.v1.websocket_endpoint import router
from dependencies import get_task_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    task_manager = get_task_manager()
    task_manager.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7878, reload=True)