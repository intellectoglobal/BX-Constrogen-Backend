from django.urls import path
from .views import (StateViewset, CityViewset)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'geolocation'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']


urlpatterns = [
    path('state/',
         StateViewset.as_view(GET_POST), name="states"),
    path('state/<int:pk>',
         StateViewset.as_view(RETRIVE_UPDATE_DELETE), name="state"),
    path('city/',
         CityViewset.as_view(GET_POST), name="cities"),
    path('city/<int:pk>',
         CityViewset.as_view(RETRIVE_UPDATE_DELETE), name="city"),
]
