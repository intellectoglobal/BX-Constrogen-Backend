from django.urls import path
from .views import (CustomerViewset, CustomerPurchaseReceiptViewset,
                    SaleAgreementViewSet, ActiveCustomerViewset, SaleInvoiceViewSet, SaleInvoiceAllView, SalePaymentAllViewSet, SourceOfFundViewSet, SaleReceiptViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT
app_name = 'sale'


GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE = ENDPOINT_METHODS_DICT['RETRIVE']
RETRIVE_UPDATE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('customer/',
         CustomerViewset.as_view(GET_POST), name="customers"),
    path('customer/<int:pk>',
         CustomerViewset.as_view(RETRIVE_UPDATE_DELETE), name="customer"),

    path('customer_purchase_receipt/',
         CustomerPurchaseReceiptViewset.as_view(GET_POST), name="customer_purchase_receipt"),
    path('customer_purchase_receipt/<int:pk>',
         CustomerPurchaseReceiptViewset.as_view(RETRIVE_UPDATE_DELETE), name="customer_purchase_receipt"),

    path('agreement/',
         SaleAgreementViewSet.as_view(GET_POST), name="agreements"),
    path('agreement/<int:pk>',
         SaleAgreementViewSet.as_view(RETRIVE_UPDATE_DELETE), name="agreement"),

    path('invoice/',
         SaleInvoiceViewSet.as_view(GET_POST), name="sale_invoices"),
    path('invoice/<str:pk>',
         SaleInvoiceViewSet.as_view(RETRIVE_UPDATE_DELETE), name="sale_invoice"),

    path('sale_invoice/all', SaleInvoiceAllView.as_view(), name='sale_invoice_all'),

    path('payment/all', SalePaymentAllViewSet.as_view(GET), name='sale_payment_all'),
    
    path('source_of_fund/',
          SourceOfFundViewSet.as_view(GET_POST), name="source_of_fund"),
    path('source_of_fund/<int:pk>',
          SourceOfFundViewSet.as_view(RETRIVE_UPDATE_DELETE), name="source_of_fund"),

    path('sale_receipt/',
          SaleReceiptViewSet.as_view(GET_POST), name="sale_receipt"),
    path('sale_receipt/<int:pk>',
          SaleReceiptViewSet.as_view(RETRIVE_UPDATE_DELETE), name="sale_receipt"),

    path('customer/all/active/',
         ActiveCustomerViewset.as_view(GET), name="active"),

]
