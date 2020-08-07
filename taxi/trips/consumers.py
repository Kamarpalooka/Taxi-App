"""
A Channels consumer is like a Django view with extra steps to support the WebSocket protocol.
Connect to channels router
"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from trips.serializers import NestedTripSerializer, TripSerializer


class TaxiConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def _get_user_group(self, user):
        return user.groups.first().name

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            user_group = await self._get_user_group(user)
            if user_group == 'driver':
                await self.channel_layer.group_add(
                    group='drivers',
                    channel=self.channel_name
                )
            await self.accept()

    async def receive_json(self, content, **kwargs):
        """
        Receives all incoming request from rider / create trip
        """
        message_type = content.get('type')
        if message_type == 'create.trip':
            await self.create_trip(content)
        elif message_type == 'echo.message':
            await self.echo_message(content)

    async def create_trip(self, message):
        data = message.get('data')
        trip = await self._create_trip(data)
        await self.send_json({
            'type': 'echo.message',
            'data': NestedTripSerializer(trip).data,
        })

    async def echo_message(self, message):
        await self.send_json(message)

    @database_sync_to_async
    def _create_trip(self, data):
        serializer = TripSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(serializer.validated_data)

    async def disconnect(self, code):
        user = self.scope['user']
        user_group = await self._get_user_group(user)
        if user_group == 'driver':
            await self.channel_layer.group_discard(
                group='drivers',
                channel=self.channel_name
            )
        await super().disconnect(code)
