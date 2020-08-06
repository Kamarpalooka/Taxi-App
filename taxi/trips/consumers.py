"""
A Channels consumer is like a Django view with extra steps to support the WebSocket protocol.
Connect to channels router
"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class TaxiConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        await super().disconnect(code)