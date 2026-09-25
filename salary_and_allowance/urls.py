from django.urls import path
from buildiq.utils import ENDPOINT_METHODS_DICT
from .views import SalaryAndAllowanceViewSet
app_name = 'salary_and_allowance'

GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('',
         SalaryAndAllowanceViewSet.as_view(GET_POST), name="salary_and_allowance"),
    path('<str:pk>',
         SalaryAndAllowanceViewSet.as_view(RETRIVE_UPDATE_DELETE), name="salary_and_allowance"),
]
