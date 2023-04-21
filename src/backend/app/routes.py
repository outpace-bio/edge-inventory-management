from awsiot.greengrasscoreipc import connect
from awsiot.greengrasscoreipc.model import (
    PublishToIoTCoreRequest, QOS, SubscribeToIoTCoreRequest
)
from fastapi import APIRouter, WebSocket
from json import dumps as json_dumps

from .core import SubscribeTopicHandler
from .settings import settings


router = APIRouter()


@router.websocket("publish")
async def handle_message(message: str) -> None:
    """
    Publish a message to a topic on AWS IoT Core.
    """
    ipc_client = connect()

    topic = f"{settings.AWS_IOT_THING_NAME}/publish"
    data = { "msg": message }

    publish_operation = ipc_client.new_publish_to_iot_core()
    publish_operation.activate(
        request=PublishToIoTCoreRequest(
            topic_name=topic,
            qos=QOS.AT_MOST_ONCE,
            payload=json_dumps(data).encode()
        )
    )


@router.websocket("subscribe")
async def handle_message(websocket: WebSocket) -> None:
    """
    Subscribe to a topic on AWS IoT Core.
    """
    ipc_client = connect()

    subscribe_operation = ipc_client.new_subscribe_to_iot_core(
        stream_handler=SubscribeTopicHandler(websocket)
    )
    subscribe_operation.activate(
        request=SubscribeToIoTCoreRequest(
            topic_name=f"{settings.AWS_IOT_THING_NAME}/subscribe",
            qos=QOS.AT_LEAST_ONCE
        )
    )