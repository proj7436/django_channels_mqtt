from django.urls import re_path
from .consumers import Boardcart


websocket_urlpatterns = [
    re_path('ws/connect', Boardcart.as_asgi())
]