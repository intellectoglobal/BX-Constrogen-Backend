from django.urls import path
from .views import (TdsEntryViewSet, TdsReportViewSet, SalesTdsViewSet, PurchaseGstEntryViewSet, PurchaseGstReportViewSet, SalesGstEntryViewSet, SalesGstReportViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'tax'

GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('purchase_tds_entry/', TdsEntryViewSet.as_view(), name='purchase_tds_entries'),
    path('purchase_tds_entry/<int:pk>/', TdsEntryViewSet.as_view(), name='purchase_tds_entry'),

    path('purchase_tds_report/', TdsReportViewSet.as_view(), name="purchase_tds_reports"),
    path('purchase_tds_report/<int:pk>/', TdsReportViewSet.as_view(), name='purchase_tds_report'),

    path('sale_tds/', SalesTdsViewSet.as_view(), name="sales_tds"),
    path('sale_tds/<int:pk>/', SalesTdsViewSet.as_view(), name='sales_tds'),

    path('purchase_gst_entry/', PurchaseGstEntryViewSet.as_view(), name='purchase_gst_entries'),
    path('purchase_gst_entry/<int:pk>/', PurchaseGstEntryViewSet.as_view(), name='purchase_gst_entry'),

    path('purchase_gst_report/', PurchaseGstReportViewSet.as_view(), name="purchase_gst_reports"),
    path('purchase_gst_report/<int:pk>/', PurchaseGstReportViewSet.as_view(), name='purchase_gst_report'),
    
    path('sales_gst_entry/', SalesGstEntryViewSet.as_view(), name='sales_gst_entries'),
    path('sales_gst_entry/<int:pk>/', SalesGstEntryViewSet.as_view(), name='sales_gst_entry'),

    path('sales_gst_report/', SalesGstReportViewSet.as_view(), name="sales_gst_reports"),
    path('sales_gst_report/<int:pk>/', SalesGstReportViewSet.as_view(), name='sales_gst_report'),
]
