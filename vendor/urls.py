from django.urls import path
from .views import (VendorTypeViewset, VendorGroupViewset,
                    ApTermsViewset, VendorViewset, VendorAllViewset, VendorPaymentAllViewSet, VendorInvAllocAmtView, VendorVoucherViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'vendor'

GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('type/',
         VendorTypeViewset.as_view(GET_POST), name="vendor_types"),
    path('type/<str:pk>',
         VendorTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="vendor_type"),

    path('group/',
         VendorGroupViewset.as_view(GET_POST), name="vendor_groups"),
    path('group/<str:pk>',
         VendorGroupViewset.as_view(RETRIVE_UPDATE_DELETE), name="vendor_group"),

    path('ap_term/',
         ApTermsViewset.as_view(GET_POST), name="ap_terms"),
    path('ap_term/<str:pk>',
         ApTermsViewset.as_view(RETRIVE_UPDATE_DELETE), name="ap_term"),

    path('vendor/all/active/',
         VendorAllViewset.as_view(GET), name="vendorsall"),
    path('vendor/',
         VendorViewset.as_view(GET_POST), name="vendors"),
    path('vendor/<str:pk>',
         VendorViewset.as_view(RETRIVE_UPDATE_DELETE), name="vendor"),
    path('payment/all', VendorPaymentAllViewSet.as_view(GET), name='vendor_payment_all'),
    path('inv_alloc_amt/',
         VendorInvAllocAmtView.as_view(GET_POST), name="vendor_inv_alloc_amt"),
    path('inv_alloc_amt/<str:pk>',
         VendorInvAllocAmtView.as_view(RETRIVE_UPDATE_DELETE), name="vendor_inv_alloc_amt"),
    path('payment/',
         VendorVoucherViewSet.as_view(GET_POST), name="vendor_payment"),
    path('payment/<str:pk>',
         VendorVoucherViewSet.as_view(RETRIVE_UPDATE_DELETE), name="vendor_payment"),
]
