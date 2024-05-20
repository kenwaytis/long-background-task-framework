import time
import random
import multiprocessing

def long_running_task(task_id: str, queue: multiprocessing.Queue):
    while True:
        result = f"Task {task_id}: Result {random.randint(1, 100)}"
        print(f"Result: {result}")
        msg = {
            "task_id": task_id,
            "content": result,
        }
        queue.put(msg)
        time.sleep(1)
