from django.urls import path
from .views import (PurchaseInquiryViewset)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'inventory'

GET = ENDPOINT_METHODS_DICT['GET']


urlpatterns = [
    path('purchase/',
         PurchaseInquiryViewset.as_view(GET), name="purchaseinquiries"),
]
