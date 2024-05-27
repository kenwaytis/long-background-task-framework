import json
import asyncio
import multiprocessing
import aiohttp

from services.business.long_running_task import long_running_task


class TaskManager:
    def __init__(self) -> None:
        self.active_connections = {}
        self.msg_queue = multiprocessing.Queue()
        self.command_queue = multiprocessing.Queue()

    async def init_queue(self):
        asyncio.create_task(self.process_msg())
        asyncio.create_task(self.process_command())
        print("TaskManager init success")

    async def process_msg(self):
        async with aiohttp.ClientSession() as session:
            while True:
                msg = await asyncio.get_event_loop().run_in_executor(None, self.msg_queue.get)
                try:
                    task_id = str(msg["task_id"])
                    url = self.active_connections[task_id]["callback_url"]
                    # content = json.dumps(msg['content'])
                    async with session.post(
                        url, json={"task_id": task_id, "content": msg["content"]}
                    ) as resp:
                        await resp.text()
                except Exception as e:
                    print(e)

    async def process_command(self):
        while True:
            command = await asyncio.get_event_loop().run_in_executor(None, self.command_queue.get)
            if command["action"] == "stop":
                self.stop_process(command["task_id"])

    def start_process(self, task_id, data, callback_url):
        if task_id in self.active_connections:
            print(f"{task_id} is already running")
            return False
        p = multiprocessing.Process(
            target=long_running_task, args=(self.msg_queue, task_id, data)
        )
        p.start()
        self.active_connections[task_id] = {"instance": p, "callback_url": callback_url}
        return True

    def stop_process(self, task_id):
        if task_id not in self.active_connections:
            print(f"{task_id} is not running")
            return False
        p = self.active_connections[task_id]["instance"]
        p.kill()
        p.join()
        del self.active_connections[task_id]
        return True

    async def shutdown(self):
        for task_id, connection in self.active_connections.items():
            self.stop_process(task_id)
