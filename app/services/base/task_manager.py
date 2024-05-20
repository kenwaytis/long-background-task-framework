import multiprocessing
from fastapi import WebSocket
from typing import Dict
from services.business.long_running_task import long_running_task

class TaskManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.processes: Dict[int, multiprocessing.Process] = {}
        self.queues: Dict[int, multiprocessing.Queue] = {}

    async def connect(self, websocket: WebSocket, task_id: int):
        await websocket.accept()
        self.active_connections[task_id] = websocket

    def disconnect(self, task_id: int):
        if task_id in self.active_connections:
            del self.active_connections[task_id]
        self.stop_process(task_id)

    async def send_message(self, task_id: int, message: str):
        websocket = self.active_connections.get(task_id)
        if websocket:
            await websocket.send_text(message)

    def start_process(self, task_id: int):
        queue = multiprocessing.Queue()
        self.queues[task_id] = queue
        process = multiprocessing.Process(target=long_running_task, args=(task_id, queue))
        process.start()
        self.processes[task_id] = process
        # 启动一个线程从队列中读取消息并发送
        process_listener = multiprocessing.Process(target=self.listen_to_queue, args=(task_id,))
        process_listener.start()

    def stop_process(self, task_id: int):
        if task_id in self.processes:
            self.processes[task_id].terminate()
            del self.processes[task_id]
        if task_id in self.queues:
            del self.queues[task_id]

    def shutdown(self):
        for task_id in list(self.processes.keys()):
            self.stop_process(task_id)

    def listen_to_queue(self, task_id: int):
        queue = self.queues.get(task_id)
        while True:
            if queue:
                message = queue.get()
                websocket = self.active_connections.get(task_id)
                if websocket:
                    websocket.send_text(message)
