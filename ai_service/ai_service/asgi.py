# """
# ASGI config for ai_service project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_service.settings")

# application = get_asgi_application()

# ai_service/ai_service/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ai.routing  # Import your app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_service.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(  # Handles WebSocket requests
        URLRouter(
            ai.routing.websocket_urlpatterns
        )
    ),
})