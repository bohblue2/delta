import zmq.asyncio

from delta.network.base import BaseNetworkPublisher

zmq_ctx = zmq.asyncio.Context()


class ZmqPublisher(BaseNetworkPublisher):
    def __init__(self, endpoint: str):
        self._endpoint = endpoint
        self._socket = zmq_ctx.socket(zmq.PUB)
        self._socket.connect(self._endpoint)

    async def publish(self, topic: str, msg: bytes, encoding="utf-8", sep=b" "):
        await self._socket.send(topic.encode(encoding) + sep + msg)

    def __del__(self):
        self._socket.close()
        zmq_ctx.term()
