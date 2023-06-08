from datetime import datetime
import json
from awsiot.greengrasscoreipc import connect
from awsiot.greengrasscoreipc.model import (
    PublishToIoTCoreRequest, QOS, SubscribeToIoTCoreRequest
)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from json import dumps as json_dumps

from .core import ConnectionManager, SubscribeTopicHandler
from .settings import settings


router = APIRouter()

manager = ConnectionManager()
topic = f"{settings.AWS_IOT_THING_NAME}/publish"

@router.websocket("/ws")
async def handle_message(websocket: WebSocket) -> None:
    """
    Subscribe to a topic on AWS IoT Core.
    """
    await manager.connect(websocket)

    now = datetime.now()
    current_time = now.strftime("%H:%M")

    try:
        while True:
            data = await websocket.receive_text()

            ipc_client = connect()

            message = { "time": current_time, "message": data }

            publish_operation = ipc_client.new_publish_to_iot_core()
            publish_operation.activate(
                request=PublishToIoTCoreRequest(
                    topic_name=topic,
                    qos=QOS.AT_MOST_ONCE,
                    payload=json_dumps(data).encode()
                )
            )

            subscribe_operation = ipc_client.new_subscribe_to_iot_core(
                stream_handler=SubscribeTopicHandler(websocket)
            )
            subscribe_operation.activate(
                request=SubscribeToIoTCoreRequest(
                    topic_name=f"{settings.AWS_IOT_THING_NAME}/subscribe",
                    qos=QOS.AT_LEAST_ONCE
                )
            )
            
            await manager.broadcast(json.dumps(message))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        message = {"time":current_time, "message":"Offline"}
        await manager.broadcast(json.dumps(message))