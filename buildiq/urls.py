from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='Builder API')

urlpatterns = [
    path('swagger-ui/', schema_view),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='API')),
    path('auth/', include('users.urls', namespace='users')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
