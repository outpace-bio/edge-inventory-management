from awsiot.greengrasscoreipc import connect
from awsiot.greengrasscoreipc.client import SubscribeToIoTCoreStreamHandler
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage, QOS, SubscribeToIoTCoreRequest
)
from fastapi import WebSocket
from logging import getLogger
from typing import Any, Dict, List
from json import loads as json_loads

from .settings import settings


class SubscribeTopicHandler(SubscribeToIoTCoreStreamHandler):
    """
    Event handler for SubscribeToTopicOperation

    Inherit from this class and override methods to handle
    stream events during a SubscribeToTopicOperation.
    """

    def __init__(self, websocket: WebSocket) -> None:
        """
        The constructor for the SubscribeTopicHandler class.

        Args:
            websocket (WebSocket): WebSocket connection for subscribing to the
                topic.
        """
        super().__init__()
        self._socket = websocket
        self._logger = getLogger(__name__)

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        """
        Invoked when a SubscriptionResponseMessage is received.

        Args:
            event (IoTCoreMessage): The message received from the subscribed
                topic.

        Postconditions:
            - The message is sent to the WebSocket connection.
        """
        payload = {
            "payload": json_loads(event.message.payload.decode())
        }

        self._socket.send_json(payload)
        self._logger.info("Message sent from SubscribeTopicHandler!")


def subscribe_to_topic(websocket: WebSocket) -> None:
    """
    Subscribe to a topic on AWS IoT Core.

    Args:
        websocket (WebSocket): WebSocket connection for subscribing to the
            topic.
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


class ConnectionManager:
    """
    Manages WebSocket connections.
    """

    def __init__(self) -> None:
        """
        The constructor for the ConnectionManager class.
        """
        self._active_conns: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Connects to the specified WebSocket.

        Args:
            websocket (WebSocket): WebSocket connection to connect to.
        """
        await websocket.accept()
        self._active_conns.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnects from the specified WebSocket.

        Args:
            websocket (WebSocket): WebSocket connection to disconnect from.

        Postcondition:
            - The specified WebSocket connection is removed from the list of
              active connections.
        """
        self._active_conns.remove(websocket)

    async def send_message(
        self, message: Dict[str, Any], websocket: WebSocket
    ) -> None:
        """
        Sends a message to the specified WebSocket.

        Args:
            message (Dict[str, Any]): The message to send.
            websocket (WebSocket): The WebSocket connection to send the message
                to.

        Postcondition:
            - The specified WebSocket connection receives the message.
        """
        await websocket.send_json(message)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcasts a message to all active WebSocket connections.

        Args:
            message (Dict[str, Any]): The message to send.

        Postcondition:
            - All active WebSocket connections receive the message.
        """
        for connection in self._active_conns:
            await self.send_message(message, connection)