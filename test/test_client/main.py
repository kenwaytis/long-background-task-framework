from contextlib import asynccontextmanager
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from aiohttp import ClientSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 立即启动后台任务，不阻塞应用启动
    asyncio.create_task(start_task())
    yield


app = FastAPI(lifespan=lifespan)


async def start_task():
    await asyncio.sleep(2)
    async with ClientSession() as session:
        task_start_request = {
            "task_id": "1",
            "data": {"rtsp_addr": "rtmp://192.168.100.50/live/livestream2"},
            "callback_url": "http://192.168.100.18:6532/callback",
        }
        async with session.post(
            "http://192.168.100.18:7878/api/v1/tasks/start", json=task_start_request
        ) as response:
            result = await response.json()
            print("Start Task Response:", result)
    # 18秒后停止任务
    await asyncio.sleep(18)
    await stop_task()


async def stop_task():
    async with ClientSession() as session:
        task_stop_request = {"task_id": "1"}
        async with session.post(
            "http://192.168.100.18:7878/api/v1/tasks/stop", json=task_stop_request
        ) as response:
            result = await response.json()
            print("Stop Task Response:", result)


@app.post("/callback")
async def callback(request: Request):
    data = await request.json()
    print(f"Callback received: {data}")
    return {"message": "Callback received"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6532)
