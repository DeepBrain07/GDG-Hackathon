import os
import django
from django.core.asgi import get_asgi_application

# 1. Set settings and initialize Django IMMEDIATELY
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'base.settings.development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup() 

# 2. Initialize the HTTP application
django_asgi_app = get_asgi_application()

# 3. Import Channels components ONLY AFTER django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from base.middleware import JWTAuthMiddleware
from apps.core.routing import websocket_urlpatterns 

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware( 
        URLRouter(
            websocket_urlpatterns
        )
    ),
})