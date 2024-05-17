from fastapi import WebSocket, WebSocketDisconnect
from task_manager import TaskManager
import json
import logging

logger = logging.getLogger(__name__)

async def websocket_endpoint(websocket: WebSocket, device_id: str, task_manager: TaskManager):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                command = data.get("command")
                rtsp_url = data.get("rtsp_url")
                if command == "start" and rtsp_url:
                    await task_manager.start_task(device_id, rtsp_url)
                    await websocket.send_text(f"Task started for device {device_id}")
                elif command == "cancel":
                    await task_manager.cancel_task(device_id)
                    await websocket.send_text(f"Task cancelled for device {device_id}")
                else:
                    await websocket.send_text(f"Invalid command for device {device_id}")
            except json.JSONDecodeError:
                await websocket.send_text(f"Invalid JSON data for device {device_id}")
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
    except WebSocketDisconnect:
        logger.info(f"Device {device_id} disconnected")
        await task_manager.cancel_task(device_id)
    except Exception as e:
        logger.error(f"Exception in WebSocket connection for device {device_id}: {e}")
        await task_manager.cancel_task(device_id)

def get_task_manager():
    return TaskManager()
