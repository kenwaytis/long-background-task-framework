from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.base.task_manager import TaskManager
from dependencies import get_task_manager
import json

router = APIRouter()

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str, task_manager: TaskManager = Depends(get_task_manager)):
    await websocket.accept()
    try:
        receive_data = await websocket.receive_text()
        data = json.loads(receive_data)
        if data.get("action") == "start":
            task_manager.start_process(websocket, task_id, data.get("data"))
        while True:
            receive_data = await websocket.receive_text()
            try:
                data = json.loads(receive_data)
                print(data)
                if data.get("action") == "stop":
                    task_manager.stop_process(task_id)
                    await websocket.close()
                    break
            except json.JSONDecodeError:
                print("Received non-JSON message")
    except WebSocketDisconnect:
        task_manager.stop_process(task_id)
        await websocket.close()
