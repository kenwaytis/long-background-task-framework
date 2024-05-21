import asyncio
import websockets
import json

async def send_command(uri, command, rtsp_url=None):
    async with websockets.connect(uri) as websocket:
        # 构建要发送的JSON数据
        data = {
            "command": command
        }
        if rtsp_url:
            data["rtsp_url"] = rtsp_url

        # 发送JSON数据
        await websocket.send(json.dumps(data))
        print(f"Sent: {data}")

        async def receive_responses():
            while True:
                response = await websocket.recv()
                print(f"Received: {response}")

        async def send_stop_command():
            await asyncio.sleep(10)
            stop_command = {
                "action": "stop"
            }
            await websocket.send(json.dumps(stop_command))
            print(f"Sent: {stop_command}")

        # 同时启动接收响应和发送停止命令的任务
        await asyncio.gather(receive_responses(), send_stop_command())

# 设备ID
device_id = 2

# WebSocket服务器的URL
uri = f"ws://192.168.100.18:7878/ws/{device_id}"

# 要发送的命令和RTSP URL
command = "start"
rtsp_url = "rtmp://192.168.100.50/live/livestream"

# 启动事件循环并发送命令
asyncio.get_event_loop().run_until_complete(send_command(uri, command, rtsp_url))
