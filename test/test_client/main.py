import asyncio
import websockets
import json


async def send_command(uri, task_id, rtsp_url):
    async with websockets.connect(uri) as websocket:
        # 构建要发送的启动命令
        start_command = {"action": "start", "data": {"rtsp_addr": rtsp_url}}

        # 连接成功2秒后发送启动命令
        await asyncio.sleep(2)
        await websocket.send(json.dumps(start_command))
        print(f"Sent: {start_command}")

        async def receive_responses():
            try:
                while True:
                    response = await websocket.recv()
                    print(f"Received: {response}")
            except websockets.exceptions.ConnectionClosedOK:
                print("Connection closed normally")

        async def send_stop_command():
            await asyncio.sleep(20)  # 因为已经等了2秒，所以再等8秒，总共10秒
            stop_command = {"action": "stop"}
            await websocket.send(json.dumps(stop_command))
            print(f"Sent: {stop_command}")

        # 同时启动接收响应和发送停止命令的任务
        await asyncio.gather(receive_responses(), send_stop_command())


# 任务ID
task_id = 2

# WebSocket服务器的URL
uri = f"ws://192.168.100.18:7878/ws/{task_id}"

# RTSP URL
rtsp_url = "rtmp://192.168.100.50/live/livestream2"

# 启动事件循环并发送命令
asyncio.get_event_loop().run_until_complete(send_command(uri, task_id, rtsp_url))
