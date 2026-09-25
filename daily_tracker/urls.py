from django.urls import path
from .views import DailyWorkProgressViewSet
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'daily_tracker'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']
urlpatterns = [
    path('daily_progress/',
         DailyWorkProgressViewSet.as_view(GET_POST), name="daily_progress"),
    path('daily_progress/<int:pk>',
         DailyWorkProgressViewSet.as_view(RETRIVE_UPDATE_DELETE), name="daily_progress"),
]
