import os
import asyncio
import multiprocessing
import signal
from multiprocessing import Process, Manager
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self):
        self.manager = Manager()
        self.tasks: Dict[str, Process] = {}
        self.cancel_events: Dict[str, Any] = self.manager.dict()
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum=None, frame=None):
        logger.info("Shutting down gracefully...")
        for device_id in list(self.tasks.keys()):
            asyncio.run(self.cancel_task(device_id))
        self.manager.shutdown()
        os._exit(0)

    async def start_task(self, device_id: str, rtsp_url: str):
        if device_id in self.tasks:
            await self.cancel_task(device_id)
        cancel_event = self.manager.Event()
        process = Process(target=self.process_stream, args=(device_id, rtsp_url, cancel_event))
        self.tasks[device_id] = process
        self.cancel_events[device_id] = cancel_event
        process.start()
        logger.info(f"Started task for device {device_id}")

    async def cancel_task(self, device_id: str):
        if device_id in self.tasks:
            self.cancel_events[device_id].set()
            self.tasks[device_id].join()
            del self.tasks[device_id]
            del self.cancel_events[device_id]
            logger.info(f"Task for device {device_id} cancelled")

    @staticmethod
    def process_stream(device_id: str, rtsp_url: str, cancel_event: Any):
        import cv2
        logger.info(f"Starting stream processing for device {device_id} with RTSP URL {rtsp_url}")
        cap = cv2.VideoCapture(rtsp_url)
        try:
            while not cancel_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break
                # 模型推理、绘制帧和推流的逻辑
                # 这里只是示例，需要替换为实际的处理逻辑
                logger.info(f"Processing stream for device {device_id}")
        except Exception as e:
            logger.error(f"Exception in process_stream for device {device_id}: {e}")
        finally:
            cap.release()
            logger.info(f"Finished processing stream for device {device_id}")

def get_task_manager():
    return TaskManager()