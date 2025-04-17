from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/movie/<slug:movie>/<slug:theater>/<str:show_time>/', consumers.MovieConsumer.as_asgi()),
]