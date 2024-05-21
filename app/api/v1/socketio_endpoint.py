import socketio
from fastapi import Depends
from services.base.task_manager import TaskManager
from dependencies import get_task_manager

sio = socketio.AsyncServer(async_mode='asgi')
task_manager = get_task_manager()

@sio.event
async def connect(sid, environ):
    print(f'Client connected: {sid}')
    path = environ['asgi.scope']['path']
    if path.startswith('/sio/'):
        task_id = path.split('/')[-1]
        print(1)
        async def send_message(content):
            await sio.emit('task_message', content, room=sid)

        if task_id in task_manager.active_connections:
            task_manager.active_connections[task_id]["event_emitter"].on("task_message", send_message)
        else:
            await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    print(f'Client disconnected: {sid}')

@sio.event
async def join(sid, data):
    print(f'Client joined: {sid}')
    task_id = data.get('task_id')
    async def send_message(content):
        await sio.emit('task_message', content, room=sid)

    if task_id in task_manager.active_connections:
        task_manager.active_connections[task_id]["event_emitter"].on("task_message", send_message)
    else:
        if not task_manager.start_process(task_id, data.get("data")):
            await sio.disconnect(sid)
            return
        task_manager.active_connections[task_id]["event_emitter"].on("task_message", send_message)

@sio.event
async def stop(sid, data):
    print(f'Client stopped: {sid}')
    task_id = data.get('task_id')
    task_manager.stop_process(task_id)
    await sio.disconnect(sid)
