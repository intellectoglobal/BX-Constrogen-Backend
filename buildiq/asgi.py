import os
import django
from django.core.asgi import get_asgi_application
import socketio
from bill_extraction.sockets import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buildiq.settings')
django.setup()

django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app)
