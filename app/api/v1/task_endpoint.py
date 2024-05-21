from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.base.task_manager import TaskManager
from dependencies import get_task_manager

router = APIRouter()


class TaskStartRequest(BaseModel):
    task_id: str
    data: dict
    callback_url: str


class TaskStopRequest(BaseModel):
    task_id: str


@router.post("/tasks/start")
async def start_task(
    request: TaskStartRequest, task_manager: TaskManager = Depends(get_task_manager)
):
    if not task_manager.start_process(
        request.task_id, request.data, request.callback_url
    ):
        raise HTTPException(status_code=400, detail="Task is already running")
    return {"message": "Task started"}


@router.post("/tasks/stop")
async def stop_task(
    request: TaskStopRequest, task_manager: TaskManager = Depends(get_task_manager)
):
    if not task_manager.stop_process(request.task_id):
        raise HTTPException(status_code=400, detail="Task is not running")
    return {"message": "Task stopped"}
