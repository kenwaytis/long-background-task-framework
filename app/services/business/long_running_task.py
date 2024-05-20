import time
import random
import multiprocessing

def long_running_task(task_id: int, queue: multiprocessing.Queue):
    while True:
        result = f"Task {task_id}: Result {random.randint(1, 100)}"
        queue.put(result)
        time.sleep(1)
