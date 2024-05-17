from fastapi import FastAPI, WebSocket
from websocket_handler import websocket_endpoint, get_task_manager

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    app.state.task_manager = get_task_manager()

@app.websocket("/ws/{device_id}")
async def websocket_router(websocket: WebSocket, device_id: str):
    await websocket_endpoint(websocket, device_id, app.state.task_manager)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6363)
