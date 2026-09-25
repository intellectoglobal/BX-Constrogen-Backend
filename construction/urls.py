from django.urls import path
from .views import (ConstructionAgreementViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'construction'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('agreement/',
         ConstructionAgreementViewSet.as_view(GET_POST), name="agreement"),
    path('agreement/<int:pk>',
         ConstructionAgreementViewSet.as_view(RETRIVE_UPDATE_DELETE), name="agreement"),
    
]
