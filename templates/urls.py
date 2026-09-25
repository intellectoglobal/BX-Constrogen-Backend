from django.urls import path
from .views import (ContractServiceTemplateViewSet,PaymentScheduleTemplateViewSet, ItemKitTemplateViewSet, CustomerPaymentScheduleTemplateViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'templates'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('contract_service/',
         ContractServiceTemplateViewSet.as_view(GET_POST), name="contract_service"),
    path('contract_service/<int:pk>',
         ContractServiceTemplateViewSet.as_view(RETRIVE_UPDATE_DELETE), name="contract_service"),
    
    path('payment_schedule/',
         PaymentScheduleTemplateViewSet.as_view(GET_POST), name="payment_schedule"),
    path('payment_schedule/<int:pk>',
         PaymentScheduleTemplateViewSet.as_view(RETRIVE_UPDATE_DELETE), name="payment_schedule"),
    
    path('item_kit/',
         ItemKitTemplateViewSet.as_view(GET_POST), name="item_kit"),
    path('item_kit/<int:pk>',
         ItemKitTemplateViewSet.as_view(RETRIVE_UPDATE_DELETE), name="item_kit"),
    
    path('customer_payment_schedule/',
         CustomerPaymentScheduleTemplateViewSet.as_view(GET_POST), name="customer_payment_schedule"),
    path('customer_payment_schedule/<int:pk>',
         CustomerPaymentScheduleTemplateViewSet.as_view(RETRIVE_UPDATE_DELETE), name="customer_payment_schedule")
]
