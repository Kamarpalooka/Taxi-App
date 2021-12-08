"""
A Channels consumer is like a Django view with extra steps to support the WebSocket protocol.
Connect to channels router
"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from trips.models import Trip
from trips.serializers import NestedTripSerializer, TripSerializer


class TaxiConsumer(AsyncJsonWebsocketConsumer):
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

            for trip_id in await self._get_trip_ids(user):
                await self.channel_layer.group_add(
                    group=trip_id,
                    channel=self.channel_name
                )

            await self.accept()

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'create.trip':
            await self.create_trip(content)
        elif message_type == 'echo.message':
            await self.echo_message(content)
        elif message_type == 'update.trip':
            await self.update_trip(content)
        elif message_type == 'cancel.trip.request':
            await self.cancel_trip(content)

    async def create_trip(self, message):
        data = message.get('data')
        trip = await self._create_trip(data)
        trip_data = NestedTripSerializer(trip).data

        # Send rider requests to all drivers.
        await self.channel_layer.group_send(
            group='drivers',
            message={
                'type': 'echo.message',
                'data': trip_data
            }
        )

        # Add rider to "trip group".
        await self.channel_layer.group_add(
            group=f'{trip.id}',
            channel=self.channel_name
        )

        # send trip info back to the user
        await self.send_json({
            'type': 'echo.message',
            'data': trip_data,
        })

    async def echo_message(self, message):
        await self.send_json(message)

    async def update_trip(self, message):
        """
        A driver accepting a request
        """
        data = message.get('data')
        trip = await self._update_trip(data)
        trip_id = f'{trip.id}'
        trip_data = NestedTripSerializer(trip).data

        # Add driver to the current trip && Send update to rider
        await self.channel_layer.group_send(
            group=trip_id,
            message={
                'type': 'echo.message',
                'data': trip_data,
            }
        )

        # Add driver to the trip group.
        await self.channel_layer.group_add(
            group=trip_id,
            channel=self.channel_name
        )

        # server sends message back to the rider
        await self.send_json({
            'type': 'echo.message',
            'data': trip_data
        })

    async def cancel_trip_request(self, message):
        """
        Rider cancels trip request after a driver acceptance and broadcast message to all drivers.
        """
        data = message.get('data')
        trip = await self._update_trip(data)
        trip_id = f'{trip.id}'
        trip_data = NestedTripSerializer(trip).data

        # Rider sends alerts to all other drivers that trip request has been accepted by other driver.
        await self.channel_layer.group_send(group='drivers', message={
            'type': 'echo.message',
            'data': trip_data
        })

        # server sends message back to WebSocket(user) the rider
        await self.send_json({
            'type': 'echo.message',
            'data': trip_data
        })

    async def disconnect(self, code):
        user = self.scope['user']

        user_group = await self._get_user_group(user)
        if user_group == 'driver':
            await self.channel_layer.group_discard(
                group='drivers',
                channel=self.channel_name
            )

        for trip_id in await self._get_trip_ids(user):
            await self.channel_layer.group_discard(
                group=trip_id,
                channel=self.channel_name
            )

        await super().disconnect(code)

    @database_sync_to_async
    def _get_user_group(self, user):
        return user.groups.first().name

    @database_sync_to_async
    def _create_trip(self, data):
        serializer = TripSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(serializer.validated_data)

    @database_sync_to_async
    def _get_trip_ids(self, user):
        """
        Get Driver / Rider related active trip(s)
        """
        user_groups = user.groups.values_list('name', flat=True)
        if 'driver' in user_groups:
            trip_ids = user.trips_as_driver.exclude(status=Trip.COMPLETED).only('id').values_list('id', flat=True)
        else:
            trip_ids = user.trips_as_rider.exclude(status=Trip.COMPLETED).only('id').values_list('id', flat=True)
        return map(str, trip_ids)

    @database_sync_to_async
    def _update_trip(self, data):
        """
        All forms of update on the trip from both driver and rider
        """
        instance = Trip.objects.get(id=data.get('id'))
        serializer = TripSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.update(instance, serializer.validated_data)

    # TODO : The rider cancels his request after a driver accepts it.
    # TODO : The server alerts all other drivers in the driver pool that someone has accepted a request.
    #  --------- solved -------
    # TODO : The driver periodically broadcasts his location to the rider during a trip.
    # TODO : The server only allows a rider to request one trip at a time.
    # TODO : The rider can share his trip with another rider, who can join the trip and receive updates.
    # TODO : The server only shares a trip request to drivers in a specific geographic location.
    # TODO : If no drivers accept the request within a certain timespan,
    # TODO : the server cancels the request and returns a message to the rider.
