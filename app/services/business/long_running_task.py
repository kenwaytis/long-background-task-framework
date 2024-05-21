import time
import cv2
import multiprocessing


def long_running_task(queue: multiprocessing.Queue, task_id: str, data):
    rtsp_addr = data.get("rtsp_addr", "")
    if not rtsp_addr:
        print(f"Task {task_id}: No RTSP address found.")
        return

    cap = cv2.VideoCapture(rtsp_addr)
    if not cap.isOpened():
        print(f"Task {task_id}: Unable to open RTSP stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Task {task_id}: Failed to read frame.")
            time.sleep(1)
            continue

        height, width = frame.shape[:2]
        result = {
            "task_id": task_id,
            "content": {"width": width, "height": height},
        }
        queue.put(result)
        print(f"Result: {result}")
        time.sleep(1)

    cap.release()
