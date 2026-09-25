from django.urls import path
from .views import (DocIdViewset, DocStatusViewset,
                    GoodsReceiptNoteViewset, GoodsReceiptNoteItemsViewset,
                    StockLedgersViewset, StockQohViewset, StockSummaryViewset,
                    ItemBatchViewset, ItemBatchLedgerViewset,
                    PurchaseTemplateViewset, PurchaseTemplateItemsViewset,
                    PurchaseOrderViewset, PurchaseOrderItemsViewset,
                    VendorInvoiceViewset, VendorinvoiceItemsViewset,
                    PaymentViewset, PaymentAllocViewset,
                    DocIdNextViewset, PurchaseTemplateAllViewset,
                    PaymentModeViewset)

from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'pricing'

GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE = ENDPOINT_METHODS_DICT['RETRIVE']
RETRIVE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_DELETE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('doc/id/next',
         DocIdNextViewset.as_view(GET), name="nextdocids"),
    path('doc/id/',
         DocIdViewset.as_view(GET_POST), name="docids"),
    path('doc/id/<str:pk>',
         DocIdViewset.as_view(RETRIVE_UPDATE_DELETE), name="docid"),

    path('doc/status/',
         DocStatusViewset.as_view(GET_POST), name="docstatuses"),
    path('doc/status/<int:pk>',
         DocStatusViewset.as_view(RETRIVE_UPDATE_DELETE), name="docstatus"),

    path('goods/receipts/',
         GoodsReceiptNoteViewset.as_view(GET_POST), name="receipts"),
    path('goods/receipts/<int:pk>',
         GoodsReceiptNoteViewset.as_view(RETRIVE_UPDATE_DELETE), name="receipt"),

    path('goods/receipts/item',
         GoodsReceiptNoteItemsViewset.as_view(GET), name="receipt_items"),
    path('goods/receipts/item/<int:pk>',
         GoodsReceiptNoteItemsViewset.as_view(RETRIVE), name="receipt_item"),

    path('stock/ledger/',
         StockLedgersViewset.as_view(GET_POST), name="stock_ledgers"),
    path('stock/ledger/<int:pk>',
         StockLedgersViewset.as_view(RETRIVE_UPDATE_DELETE), name="stock_ledger"),

    path('stock/qoh/',
         StockQohViewset.as_view(GET_POST), name="stock_qohs"),
    path('stock/qoh/<int:pk>',
         StockQohViewset.as_view(RETRIVE_UPDATE_DELETE), name="stock_qoh"),

    path('stock/summary/',
         StockSummaryViewset.as_view(GET_POST), name="stock_summarys"),
    path('stock/summary/<int:pk>',
         StockSummaryViewset.as_view(RETRIVE_UPDATE_DELETE), name="stock_summary"),

    path('item/batch/',
         ItemBatchViewset.as_view(GET_POST), name="item_batches"),
    path('item/batch/<int:pk>',
         ItemBatchViewset.as_view(RETRIVE_UPDATE_DELETE), name="item_batch"),

    path('item/batch/ledger/',
         ItemBatchLedgerViewset.as_view(GET_POST), name="item_batche_ledgers"),
    path('item/batch/ledger/<int:pk>',
         ItemBatchLedgerViewset.as_view(RETRIVE_UPDATE_DELETE), name="item_batche_ledger"),

    path('purchase/template/all/active',
         PurchaseTemplateAllViewset.as_view(GET), name="purchase_templates_all"),
    path('purchase/template/',
         PurchaseTemplateViewset.as_view(GET_POST), name="purchase_templates"),
    path('purchase/template/<int:pk>',
         PurchaseTemplateViewset.as_view(RETRIVE_UPDATE_DELETE), name="purchase_template"),

    path('purchase/template/items/',
         PurchaseTemplateItemsViewset.as_view(GET_POST), name="purchase_template_items"),
    path('purchase/template/items/<int:pk>',
         PurchaseTemplateItemsViewset.as_view(RETRIVE_DELETE), name="purchase_template_item"),

    path('purchase/order/',
         PurchaseOrderViewset.as_view(GET_POST), name="purchase_orders"),
    path('purchase/order/<int:pk>',
         PurchaseOrderViewset.as_view(RETRIVE_UPDATE_DELETE), name="purchase_order"),

    path('purchase/order/items/',
         PurchaseOrderItemsViewset.as_view(GET_POST), name="purchase_order_items"),
    path('purchase/order/items/<int:pk>',
         PurchaseOrderItemsViewset.as_view(RETRIVE), name="purchase_order_item"),

    path('vendor/invoice/items/',
         VendorinvoiceItemsViewset.as_view(GET_POST), name="vendor_invoice_items"),
    path('vendor/invoice/items/<int:pk>',
         VendorinvoiceItemsViewset.as_view(RETRIVE), name="vendor_invoice_item"),

    path('vendor/invoice/',
         VendorInvoiceViewset.as_view(GET_POST), name="vendor_invoices"),
    path('vendor/invoice/<int:pk>',
         VendorInvoiceViewset.as_view(RETRIVE_UPDATE_DELETE), name="vendor_invoice"),

    path('payment/',
         PaymentViewset.as_view(GET_POST), name="payments"),
    path('payment/<int:pk>',
         PaymentViewset.as_view(RETRIVE_UPDATE_DELETE), name="payment"),

    path('payment/mode/',
         PaymentModeViewset.as_view(GET_POST), name="paymentmodes"),
    path('payment/mode/<int:pk>',
         PaymentModeViewset.as_view(RETRIVE_UPDATE_DELETE), name="paymentmode"),

    path('payment/allocation/',
         PaymentAllocViewset.as_view(GET_POST), name="paymentallocations"),
    path('payment/allocation/<int:pk>',
         PaymentAllocViewset.as_view(RETRIVE_UPDATE_DELETE), name="paymentallocation"),
]
