from django.urls import path
from .views import (ClinetBaseViewset, CompanyViewset,
                    CostCategoryViewset, CostCodeViewset, BankAccountView)
from buildiq.utils import ENDPOINT_METHODS_DICT
app_name = 'client'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']


urlpatterns = [
    path('client/',
         ClinetBaseViewset.as_view(GET_POST), name="clients"),
    path('client/<str:pk>',
         ClinetBaseViewset.as_view(RETRIVE_UPDATE), name="client"),

    path('company/',
         CompanyViewset.as_view(GET_POST), name="companies"),
    path('company/<str:pk>',
         CompanyViewset.as_view(RETRIVE_UPDATE), name="company"),

    path('cost_category/',
         CostCategoryViewset.as_view(GET_POST), name="cost_categories"),

    path('cost_category/<int:pk>',
         CostCategoryViewset.as_view(RETRIVE_UPDATE_DELETE), name="cost_category"),

    path('cost_code/',
         CostCodeViewset.as_view(GET_POST), name="cost_categories"),

    path('cost_code/<int:pk>',
         CostCodeViewset.as_view(RETRIVE_UPDATE_DELETE), name="cost_category"),
    
    path('bank/',
         BankAccountView.as_view(GET_POST), name="bank_account"),

    path('bank/<int:pk>',
         BankAccountView.as_view(RETRIVE_UPDATE_DELETE), name="bank_account"),
    
]
