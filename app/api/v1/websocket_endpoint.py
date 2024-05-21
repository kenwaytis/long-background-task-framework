from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.base.task_manager import TaskManager
from dependencies import get_task_manager
import json

router = APIRouter()


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: str,
    task_manager: TaskManager = Depends(get_task_manager),
):
    async def send_message(content):
        await websocket.send_text(content)

    await websocket.accept()
    receive_data = await websocket.receive_text()
    data = json.loads(receive_data)
    print(data)
    # 如果任务已经在运行，则只需订阅消息
    if task_id in task_manager.active_connections:
        task_manager.active_connections[task_id]["event_emitter"].on(
            "task_message", send_message
        )
    else:
        # 如果任务未运行，启动任务并订阅消息
        if not task_manager.start_process(task_id, data.get("data")):
            await websocket.close()
            return
        task_manager.active_connections[task_id]["event_emitter"].on(
            "task_message", send_message
        )

    try:
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
    finally:
        if task_id in task_manager.active_connections:
            task_manager.active_connections[task_id]["event_emitter"].remove_listener(
                "task_message", send_message
            )
