import multiprocessing
import threading
import asyncio
from fastapi import WebSocket
from typing import Dict
from services.business.long_running_task import long_running_task

class TaskManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.processes: Dict[int, multiprocessing.Process] = {}
        self.queues: Dict[int, multiprocessing.Queue] = {}
        self.lock = threading.Lock()
        self.listener_thread = threading.Thread(target=self.listen_to_queues, daemon=True)
        self.listener_thread.start()

    async def connect(self, websocket: WebSocket, task_id: int):
        await websocket.accept()
        with self.lock:
            self.active_connections[task_id] = websocket

    def disconnect(self, task_id: int):
        with self.lock:
            if task_id in self.active_connections:
                del self.active_connections[task_id]
            self.stop_process(task_id)

    async def send_message(self, task_id: int, message: str):
        with self.lock:
            websocket = self.active_connections.get(task_id)
        if websocket:
            await websocket.send_text(message)

    def start_process(self, task_id: int):
        queue = multiprocessing.Queue()
        with self.lock:
            self.queues[task_id] = queue
        process = multiprocessing.Process(target=long_running_task, args=(task_id, queue))
        process.start()
        with self.lock:
            self.processes[task_id] = process

    def stop_process(self, task_id: int):
        with self.lock:
            if task_id in self.processes:
                self.processes[task_id].terminate()
                del self.processes[task_id]
            if task_id in self.queues:
                del self.queues[task_id]

    def shutdown(self):
        with self.lock:
            for task_id in list(self.processes.keys()):
                self.stop_process(task_id)

    def listen_to_queues(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            with self.lock:
                for task_id, queue in list(self.queues.items()):
                    if not queue.empty():
                        message = queue.get()
                        loop.run_until_complete(self.send_message(task_id, message))
