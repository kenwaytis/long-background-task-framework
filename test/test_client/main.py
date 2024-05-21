import socketio
import asyncio
import json

# 创建一个Socket.IO客户端实例
sio = socketio.AsyncClient()

# 处理连接事件
@sio.event
async def connect():
    print('Connected to server')

    # 加入任务并发送JSON数据
    join_data = {
        "task_id": "1",
        "data": {
            "rtsp_addr": "rtmp://192.168.100.50/live/livestream1"
        }
    }
    await sio.emit('join', join_data)
    print('Join event sent:', join_data)

    # 等待20秒后发送停止命令
    await asyncio.sleep(20)
    stop_data = {"task_id": "1", "action": "stop"}
    await sio.emit('stop', stop_data)
    print('Stop event sent:', stop_data)

# 处理断开连接事件
@sio.event
async def disconnect():
    print('Disconnected from server')

# 处理自定义任务消息事件
@sio.event
async def task_message(data):
    print('Task message received:', data)

# 主函数，连接到服务器并运行事件循环
async def main():
    await sio.connect('http://192.168.100.18:7878/sio/')  # 修改为你的服务器地址
    await sio.wait()

# 运行主函数
if __name__ == '__main__':
    asyncio.run(main())
