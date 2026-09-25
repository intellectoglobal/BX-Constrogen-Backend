from django.urls import path
from .views import (VendorContractViewset,
                    VendorcontractStagesViewset, VendorcontractTasksViewset, VendorContractInvoiceViewset, ContractorViewset, ContractorTypeViewset, ContractAgreementViewSet, ContractorInvoiceViewSet,ContractorInvoiceAllView, ContractInvAllocAmtView, ContractVoucherViewSet, ContractorPaymentAllViewSet)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'contract'

GET = ENDPOINT_METHODS_DICT['GET']
GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']

urlpatterns = [
    path('contractor/',
         VendorContractViewset.as_view(GET_POST), name="contracts"),
    path('contractor/<str:pk>',
         VendorContractViewset.as_view(RETRIVE_UPDATE_DELETE), name="contract"),

    path('stage/',
         VendorcontractStagesViewset.as_view(GET_POST), name="stages"),
    path('stage/<str:pk>',
         VendorcontractStagesViewset.as_view(RETRIVE_UPDATE_DELETE), name="stage"),

    path('task/',
         VendorcontractTasksViewset.as_view(GET_POST), name="tasks"),
    path('task/<str:pk>',
         VendorcontractTasksViewset.as_view(RETRIVE_UPDATE_DELETE), name="task"),

    path('invoice/',
         VendorContractInvoiceViewset.as_view(GET_POST), name="contract_invoices"),
    path('invoice/<str:pk>',
         VendorContractInvoiceViewset.as_view(RETRIVE_UPDATE_DELETE), name="contract_invoice"),

    path('type/',
         ContractorTypeViewset.as_view(GET_POST), name="contractor_types"),
    path('type/<str:pk>',
         ContractorTypeViewset.as_view(RETRIVE_UPDATE_DELETE), name="contractor_type"),

    path('contractors/',
         ContractorViewset.as_view(GET_POST), name="contractors"),
    path('contractors/<str:pk>',
         ContractorViewset.as_view(RETRIVE_UPDATE_DELETE), name="contractor"),

    path('contract_agrmnt/',
         ContractAgreementViewSet.as_view(GET_POST), name="contract_agrmnt"),
    path('contract_agrmnt/<str:pk>',
         ContractAgreementViewSet.as_view(RETRIVE_UPDATE_DELETE), name="contract_agrmnt"),

    path('contractor_invoice/all', ContractorInvoiceAllView.as_view(), name='contractor_invoice_all'),

    path('payment/all', ContractorPaymentAllViewSet.as_view(GET), name='contractor_payment_all'),
    
    path('contractor_invoice/',
         ContractorInvoiceViewSet.as_view(GET_POST), name="contractor_invoice"),
    path('contractor_invoice/<str:pk>',
         ContractorInvoiceViewSet.as_view(RETRIVE_UPDATE_DELETE), name="contractor_invoice"),

    path('inv_alloc_amt/',
         ContractInvAllocAmtView.as_view(GET_POST), name="inv_alloc_amt"),
    path('inv_alloc_amt/<str:pk>',
         ContractInvAllocAmtView.as_view(RETRIVE_UPDATE_DELETE), name="inv_alloc_amt"),
         
    path('payment/',
         ContractVoucherViewSet.as_view(GET_POST), name="contract_payment"),
    path('payment/<str:pk>',
         ContractVoucherViewSet.as_view(RETRIVE_UPDATE_DELETE), name="contract_payment"),
]