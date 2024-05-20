from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.base.task_manager import TaskManager
from dependencies import get_task_manager

router = APIRouter()

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str, task_manager: TaskManager = Depends(get_task_manager)):
    await websocket.accept()
    try:
        flag = task_manager.start_process(task_id, websocket)
        while True:
            receive_data = await websocket.receive_text()
            print(receive_data)
            if receive_data == "stop":
                task_manager.stop_process(task_id)
                await websocket.close()
                break
    except WebSocketDisconnect:
        task_manager.disconnect(task_id)
