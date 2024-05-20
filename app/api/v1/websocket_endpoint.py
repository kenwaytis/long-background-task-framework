from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.base.task_manager import TaskManager
from dependencies import get_task_manager

router = APIRouter()

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: int, task_manager: TaskManager = Depends(get_task_manager)):
    await task_manager.connect(websocket, task_id)
    try:
        task_manager.start_process(task_id)
        while True:
            data = await websocket.receive_text()
            print(data)
            if data == "stop":
                task_manager.stop_process(task_id)
                await websocket.close()
                break
    except WebSocketDisconnect:
        task_manager.disconnect(task_id)
