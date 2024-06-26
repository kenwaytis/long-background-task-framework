import json
import asyncio
import multiprocessing

from pyee import AsyncIOEventEmitter

from services.business.long_running_task import long_running_task

class TaskManager:
    """
    self.active_connections: {'{task_id}':{'instance': p, 'event_emitter': '{event_emitter}', 'task_info': '{info}'}}
    self.msg_queue: {'{task_id}': {...}}
    self.command_queue: {'action': '', 'task_id': '{task_id}'}
    """

    def __init__(self) -> None:
        self.active_connections = {}
        self.msg_queue = multiprocessing.Queue()
        self.command_queue = multiprocessing.Queue()
        self.event_emitters = {}

    async def init_queue(self):
        asyncio.create_task(self.process_msg())
        asyncio.create_task(self.process_command())
        print("TaskManager init success")

    async def process_msg(self):
        while True:
            if self.msg_queue.empty():
                await asyncio.sleep(0.01)
                continue
            msg = self.msg_queue.get()
            try:
                task_id = msg['task_id']
                content = json.dumps(msg['content'])
                if task_id in self.active_connections:
                    self.active_connections[task_id]['event_emitter'].emit('task_message', content)
            except Exception as e:
                print(e)

    async def process_command(self):
        while True:
            if self.command_queue.empty():
                await asyncio.sleep(0.01)
                continue
            command = self.command_queue.get()
            if command['action'] == 'stop':
                self.stop_process(command['task_id'])

    def start_process(self, task_id, data):
        if task_id in self.active_connections:
            print(f"{task_id} is already running")
            return False
        p = multiprocessing.Process(target=long_running_task, args=(self.msg_queue, task_id, data))
        p.start()
        event_emitter = AsyncIOEventEmitter()
        self.active_connections[task_id] = {'instance': p, 'event_emitter': event_emitter, 'task_info': ''}
        return True
    
    def stop_process(self, task_id):
        if task_id not in self.active_connections:
            print(f"{task_id} is not running")
            return False
        p = self.active_connections[task_id]['instance']
        p.kill()
        p.join()
        p.close()
        del self.active_connections[task_id]
        return True
        
