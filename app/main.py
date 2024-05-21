import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import socketio
from api.v1.socketio_endpoint import sio
from dependencies import get_task_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    task_manager = get_task_manager()
    await task_manager.init_queue()
    yield
    task_manager.shutdown()

app = FastAPI(lifespan=lifespan)
sio_app = socketio.ASGIApp(sio)
app.mount('/', sio_app)

if __name__ == "__main__":
    # import sys
    # log_file = open('./log.txt', 'w')
    # sys.stdout = log_file
    # sys.stderr = log_file
    uvicorn.run("main:app", host="0.0.0.0", port=7878)
