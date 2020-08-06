"""
A router is the Channels counterpart to Django's URL.
"""
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter

from taxi.middleware import TokenAuthMiddlewareStack
from trips.consumers import TaxiConsumer


application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('taxi/', TaxiConsumer),
        ])
    ),
})