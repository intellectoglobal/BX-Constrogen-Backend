from django.urls import path
from .views import GSTVendorInvoiceViewSet, NonGSTVendorInvoiceViewSet, CustomerPaymentReceiptReportViewSet, ContractorPaymentVoucherReportViewSet, SupplierPaymentVoucherReportViewSet, ContractorTDSReportViewSet, ExportReportViewSet, PayrollReportViewSet

app_name = 'audit_reports'

urlpatterns = [
    path('gst_vendor_invoices/', GSTVendorInvoiceViewSet.as_view(),
         name='gst_vendor_invoices'),
    path('non_gst_vendor_invoices/', NonGSTVendorInvoiceViewSet.as_view(),
         name='non_gst_vendor_invoices'),
    path('customer_payment_receipts/', CustomerPaymentReceiptReportViewSet.as_view(),
         name='customer_payment_receipts'),
    path('contractor_payment_vouchers/', ContractorPaymentVoucherReportViewSet.as_view(),
         name='contractor_payment_vouchers'),
    path('supplier_payment_vouchers/', SupplierPaymentVoucherReportViewSet.as_view(),
         name='supplier_payment_vouchers'),
    path('contractor_tds_report/', ContractorTDSReportViewSet.as_view(),
         name='contractor_tds_report'),
     path('payroll_report/',PayrollReportViewSet.as_view(),name='payroll_report'),
    path('export_report/', ExportReportViewSet.as_view(),
         name='export_report'),
]
