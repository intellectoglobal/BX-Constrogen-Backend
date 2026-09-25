from django.shortcuts import render
from .models import (Vendorcontract, VendorcontractStages, VendorcontractTasks, Contractor, ContractorType, ContractAgreement,
                     ContractAgreementService,  ContractAgreementPaymentSchedule, ContractorInvoice, ContractInvAllocAmt, ContractVoucherHdr, ContractVoucherDtl)
from .serializers import (VendorContractSerializer,
                          VendorContractStagesSerializer, VendorContractTasksSerializer, ContractorSerializer, ContractorGetSerializer, ContractorTypeSerializer, ContractAgreementSerializer, ContractAgreementServiceSerializer, ContractAgreementPaymentScheduleSerializer, ContractAgreementGetSerializer, ContractAgreementListSerializer, ContractorInvoiceSerializer, ContractInvAllocAmtSerializer, ContractVoucherHdrSerializer, ContractVoucherHdrListSerializer, ContractVoucherHdrGetSerializer, ContractVoucherDtlSerializer, ContractInvAllocAmtGetSerializer, PayContractorSerializer, PayInvoiceSerializer)

from tax.models import TdsEntry, TdsReport
from tax.serializers import TdsEntrySerializer, TdsReportSerializer

# For Contract Invoice
from pricing.models import Vendorinvoice
from pricing.serializers import VendorInvoiceSerializer, VendorInvoiceItemsSerializer
from vendor.serializers import VendorSerializer, VendorTypeSerializer
from vendor.models import Vendor, Vendortype

from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from datetime import datetime
from buildiq.utils import UtilFunctions
from buildiq.pagenation_configs import Pagination10PerPage
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from rest_framework.views import APIView
from collections import defaultdict
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper


class VendorContractViewset(viewsets.GenericViewSet):
    queryset = Vendorcontract.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = VendorContractSerializer

    def list(self, request):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(company=companyID, client_id=clientID)
        if request.GET.get('only_submitted_contracts', False) and request.GET.get('only_submitted_contracts').upper() == "TRUE":
            qrySet = qrySet.filter(docstatus="U").order_by('-key')
        else:
            qrySet = qrySet.all().order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = VendorContractSerializer(
                qrySet, many=True, fields=('key', 'docid', 'vend_key', 'contractno'))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = VendorContractSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = VendorContractSerializer(vendCntrctIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        vendCntrctIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)

        serializer = VendorContractSerializer(
            vendCntrctIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Vendor Contract Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendor Contract PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor Contract PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        reqData = request.data

        if not reqData.get('action', False):
            return Response({"error": 1, "detail": "action missing", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData['action'].upper() in ["SAVE", "SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"]:
            return Response({"error": 1, "detail": "Invalid action POST request. valid actions are SAVE,SUBMIT_WITH_SAVE,SUBMIT_WITHOUT_SAVE,CANCEL", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        CURRENT_ACTION = reqData['action'].upper()

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not reqData.get('key', False):
            return Response({"error": 1, "detail": "key (Vendor Contract Key) is required for this process", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not Vendorcontract.objects.filter(key=reqData.get('key')).exists():
            return Response({"error": 1, "detail": "Invalid Vendor Contract key", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData.get('docid', False):
            return Response({"error": 1, "detail": "docid missing. Valid docidd would be VCN", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData.get('docid').upper() == "VCN":
            return Response({"error": 1, "detail": "Invalid Doc ID, Valid Doc ID is VCN", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # SAVE PROCESS
        if CURRENT_ACTION == "SAVE":
            reqData["docstatus"] = "S"
            reqData["contractno"] = UF.getValidDocId(
                reqData['contractno'],
                reqData.get('docid'),
                clientID
            )

            if reqData.get("key", False) and Vendorcontract.objects.filter(key=reqData.get("key")):
                reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
                reqData['lastmodifieddttm'] = UF.getCurrentDateAndTime()
                reqData.pop("contractno")

                venContctIns, venContctSuccess, returnMsg, returnData = Vendorcontract.objects.updateVendorContract(
                    reqData, reqData.get("key"), VendorContractSerializer, {})
                successMsg = "Contract Modified Successfully"
            else:
                reqData['createdby'] = UF.getCurrentSessionUser(request)
                reqData['createddttm'] = UF.getCurrentDateAndTime()

                venContctIns, venContctSuccess, returnMsg, returnData = Vendorcontract.objects.saveVendorContract(
                    reqData, VendorContractSerializer)
                successMsg = "Contract Added Successfully"

            if venContctSuccess:
                reqData['vendctr_key'] = venContctIns.get("key")
                reqData['user'] = UF.getCurrentSessionUser(request)
                reqData['createdby'] = UF.getCurrentSessionUser(request)
                reqData['createddttm'] = UF.getCurrentDateAndTime()
                contSTGIns, contSTGSuccess, returnMsg1, returnData1 = Vendorcontract.objects.insertVendorContractStage(
                    reqData, VendorContractStagesSerializer)
                contTSKIns, contTSKSuccess, returnMsg2, returnData2 = Vendorcontract.objects.insertVendorContractTasks(
                    reqData, VendorContractTasksSerializer)

                if contSTGSuccess and contTSKSuccess:
                    venContctIns['vend_contract_stages'] = contSTGIns
                    venContctIns['vend_contract_tasks'] = contTSKIns
                    return Response({"error": 0, "detail": successMsg, "data": venContctIns}, status=status.HTTP_201_CREATED)
                elif not contSTGSuccess:
                    Vendorcontract.objects.rollBack(venContctIns.get("key"))
                    return Response({"error2": 0, "detail": returnMsg1, "data": returnData1}, status=status.HTTP_400_BAD_REQUEST)
                elif not contTSKSuccess:
                    Vendorcontract.objects.rollBack(venContctIns.get("key"))
                    return Response({"error3": 0, "detail": returnMsg2, "data": returnData2}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITH_SAVE":
            reqData["docstatus"] = "U"
            reqData.pop("contractno")  # prevent to change voucher number
            vendctr_key = reqData.get('key')

            reqData['submittedby'] = UF.getCurrentSessionUser(request)
            reqData['submitteddttm'] = UF.getCurrentDateAndTime()
            reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
            reqData['lastmodifieddttm'] = UF.getCurrentDateAndTime()

            venContctIns, venContctSuccess, returnMsg, returnData = Vendorcontract.objects.updateVendorContract(
                reqData, reqData.get("key"), VendorContractSerializer, {})

            if venContctSuccess:
                reqData['vendctr_key'] = vendctr_key
                reqData['user'] = UF.getCurrentSessionUser(request)
                contSTGIns, contSTGSuccess, returnMsg1, returnData1 = Vendorcontract.objects.insertVendorContractStage(
                    reqData, VendorContractStagesSerializer)
                contTSKIns, contTSKSuccess, returnMsg2, returnData2 = Vendorcontract.objects.insertVendorContractTasks(
                    reqData, VendorContractTasksSerializer)

                if contSTGSuccess and contTSKSuccess:
                    venContctIns['vend_contract_stages'] = contSTGIns
                    venContctIns['vend_contract_tasks'] = contTSKIns
                    return Response({"error": 0, "detail": "Contract Submitted Successfully", "data": venContctIns}, status=status.HTTP_201_CREATED)
                elif not contSTGSuccess:
                    Vendorcontract.objects.rollBack(venContctIns.get("key"))
                    return Response({"error": 0, "detail": returnMsg1, "data": returnData1}, status=status.HTTP_400_BAD_REQUEST)
                elif not contTSKSuccess:
                    Vendorcontract.objects.rollBack(venContctIns.get("key"))
                    return Response({"error": 0, "detail": returnMsg2, "data": returnData2}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITHOUT_SAVE":
            vendctr_key = reqData.get('key')
            vendCntrctIns = get_object_or_404(self.queryset, pk=vendctr_key)
            vendCntrctIns.docstatus = "U"
            vendCntrctIns.save()
            serializer_class = VendorContractSerializer(vendCntrctIns)
            return Response(serializer_class.data)

        # CANCEL PROCESS
        if CURRENT_ACTION == "CANCEL":
            reqData["docstatus"] = "C"
            reqData.pop("contractno")  # prevent to change voucher number
            vendctr_key = reqData.get('key')
            venContctIns, venContctSuccess, returnMsg, returnData, otherTableUpdateReq = Vendorcontract.objects.cancelVendorContract(
                request, vendctr_key, VendorContractSerializer, UF.getCurrentDateAndTime(), UF.getCurrentSessionUser(request))
            if venContctSuccess:
                return Response({"error": 0, "detail": "Contract Cancelled Successfully", "data": venContctIns}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 1, "detail": "Invalid action", "data": {}}, status=status.HTTP_400_BAD_REQUEST)


class VendorcontractStagesViewset(viewsets.ViewSet):
    queryset = VendorcontractStages.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = VendorContractStagesSerializer(
            self.queryset.filter(company=companyID, client_id=clientID), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctStgIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = VendorContractStagesSerializer(vendCntrctStgIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctStgIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        vendCntrctStgIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctStgIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)

        serializer = VendorContractStagesSerializer(
            vendCntrctStgIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Vendor Contract Stage Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendor Contract Stage PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor Contract PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = VendorContractStagesSerializer(data=request.data)
        if serializer.is_valid():

            try:
                if serializer.save():
                    return Response({"error": 0, "detail": "Vendor Contract Stage Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Vendor Contract Stage"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorcontractTasksViewset(viewsets.ViewSet):
    queryset = VendorcontractTasks.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = VendorContractTasksSerializer(
            self.queryset.filter(company=companyID, client_id=clientID), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctTskIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = VendorContractTasksSerializer(vendCntrctTskIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctTskIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        vendCntrctTskIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendCntrctTskIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer = VendorContractTasksSerializer(
            vendCntrctTskIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Vendor Contract Tasks Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendor Contract Tasks PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor Contract PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = VendorContractTasksSerializer(data=request.data)
        if serializer.is_valid():

            try:
                if serializer.save():
                    return Response({"error": 0, "detail": "Vendor Contract Tasks Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Vendor Contract Tasks"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorContractInvoiceViewset(viewsets.GenericViewSet):
    queryset = Vendorinvoice.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = VendorInvoiceSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        activeVendors = Vendor.objects.filter(
            inactive='N', company=companyID, client_id=clientID)
        ContrtVndrTypeIns = Vendortype.objects.filter(
            contractor="Y", company=companyID, client_id=clientID)

        contractorVndTypeIds = []
        if ContrtVndrTypeIns.exists():
            contractorVndTypeIds = [venType['key'] for venType in VendorTypeSerializer(
                ContrtVndrTypeIns, many=True).data]

        activeContractorVendors = [ven['key'] for ven in VendorSerializer(activeVendors.filter(
            vendtyp_key__in=contractorVndTypeIds), many=True, fields=('key',)).data]

        querySet = self.queryset.filter(
            vend_key__in=activeContractorVendors, company=companyID, client_id=clientID).order_by('-key')

        if request.GET.get('project', False):
            querySet.filter(proj_key=request.GET.get('project'))

        if request.GET.get('contractor', False):
            querySet.filter(vend_key=request.GET.get('contractor'))

        page = self.paginate_queryset(querySet)

        serializer = VendorInvoiceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        invoiceIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = VendorInvoiceSerializer(invoiceIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        invoiceIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        invoiceIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        invoiceIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer = VendorInvoiceSerializer(
            invoiceIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Contract Invoice Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Contract Invoice PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Contract Invoice PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        if not reqData.get('action', False):
            return Response({"error": 1, "detail": "action missing", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData['action'].upper() in ["SAVE", "SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"]:
            return Response({"error": 1, "detail": "Invalid action POST request. valid actions are SAVE,SUBMIT_WITH_SAVE,SUBMIT_WITHOUT_SAVE,CANCEL", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        CURRENT_ACTION = reqData['action'].upper()

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not reqData.get('key', False):
            return Response({"error": 1, "detail": "key (Vendor Invoice Key) is required for this process", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not Vendorinvoice.objects.filter(key=reqData.get('key')).exists():
            return Response({"error": 1, "detail": "Invalid Vendor Invoice key", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # SAVE PROCESS
        if CURRENT_ACTION == "SAVE":
            reqData["docstatus"] = "S"
            reqData["vouchno"] = UF.getValidDocId(
                reqData['vouchno'], "VCI", clientID)

            if reqData.get("key", False) and Vendorinvoice.objects.filter(key=reqData.get("key"), company=companyID, client_id=clientID):
                reqData.pop("vouchno")
                # reqData['balamt'] = reqData['invamt']
                invcIns, invcSuccess, returnMsg, returnData = Vendorinvoice.objects.invoiceUpdate(
                    reqData, VendorInvoiceSerializer, reqData.get("key"), {})
                onSuccessMessage = "Contract Invoice Modified Successfully"
            else:
                # reqData['balamt'] = reqData['invamt']
                invcIns, invcSuccess, returnMsg, returnData = Vendorinvoice.objects.saveInvoice(
                    reqData, VendorInvoiceSerializer)
                onSuccessMessage = "Contract Invoice Added Successfully"

            if invcSuccess:
                reqData['invoice_id'] = invcIns.get("key")
                reqData['createdby'] = UF.getCurrentSessionUser(request)
                invoiceItmIns, invoiceItmSuccess, returnMsg, returnData = Vendorinvoice.objects.insertInvoiceItems(
                    reqData, VendorInvoiceItemsSerializer)
                if invoiceItmSuccess:
                    invcIns['invoice_items'] = invoiceItmIns
                    return Response({"error": 0, "detail": onSuccessMessage, "data": invcIns}, status=status.HTTP_201_CREATED)

                # If invoice items failed to load delete invoice entry
                Vendorinvoice.objects.deleteInvoiceByInvoiceID(
                    invcIns.get("key"))

                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITH_SAVE":
            reqData["docstatus"] = "U"
            reqData.pop("vouchno")  # prevent to change voucher number
            veninv_key = reqData.get('key')

            invoiceIns, invoiceSuccess, returnMsg, returnData = Vendorinvoice.objects.submitInvoice(
                reqData, veninv_key, VendorInvoiceSerializer)
            if invoiceSuccess:
                reqData['invoice_id'] = veninv_key
                reqData['createdby'] = UF.getCurrentSessionUser(request)
                contract_key = invoiceIns.get('contract_key')

                invoiceItmIns, invoiceItmSuccess, returnMsg, returnData = Vendorinvoice.objects.insertInvoiceItems(
                    reqData, VendorInvoiceItemsSerializer)
                if invoiceItmSuccess:
                    # OTHER TABLE UPDATES
                    reqData['current_user'] = UF.getCurrentSessionUser(request)
                    reqData['current_date'] = UF.getCurrentDateAndTime()
                    isOtherTableSuccss = Vendorinvoice.objects.doOtherTableUpdatesForContractInvoice(
                        VendorInvoiceSerializer, reqData, CURRENT_ACTION, veninv_key, contract_key)
                    if isOtherTableSuccss:
                        invoiceIns['invoice_items'] = invoiceItmIns
                        return Response({"error": 0, "detail": "Invoice Submission Success", "data": invoiceIns}, status=status.HTTP_201_CREATED)
                    return Response({"error": 1, "detail": "Invalid Request. GRN_KEY might be wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITHOUT_SAVE":
            reqData["docstatus"] = "U"
            reqData.pop("vouchno")  # prevent to change voucher number
            veninv_key = reqData.get('key')
            contract_key = reqData.get('contract_key')
            reqData['current_user'] = UF.getCurrentSessionUser(request)
            reqData['current_date'] = UF.getCurrentDateAndTime()

            isOtherTableSuccss = Vendorinvoice.objects.doOtherTableUpdatesForContractInvoice(
                VendorInvoiceSerializer, reqData, CURRENT_ACTION, veninv_key, contract_key)
            if isOtherTableSuccss:
                VendorinvoiceIns = get_object_or_404(
                    self.queryset, pk=veninv_key)
                serializer_class = VendorInvoiceSerializer(VendorinvoiceIns)
                return Response({"error": 0, "detail": "Invoice Submission Success", "data": serializer_class.data}, status=status.HTTP_201_CREATED)
            return Response({"error": 1, "detail": "Invalid Request. GRN_KEY might be wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # CANCEL PROCESS
        if CURRENT_ACTION == "CANCEL":
            reqData["docstatus"] = "C"
            # prevent to change voucher number invoiceIns
            reqData.pop("vouchno")
            veninv_key = reqData.get('key')
            contract_key = reqData.get('contract_key')

            invoiceIns, invoiceCanclSucss, returnMsg, returnData, otherTableUpdateReq = Vendorinvoice.objects.cancelInvoice(
                veninv_key, VendorInvoiceSerializer)
            if invoiceCanclSucss and otherTableUpdateReq:
                reqData['current_user'] = UF.getCurrentSessionUser(request)
                reqData['current_date'] = UF.getCurrentDateAndTime()
                isOtherTableSuccss = Vendorinvoice.objects.doOtherTableUpdatesForContractInvoice(
                    VendorInvoiceSerializer, reqData, CURRENT_ACTION, veninv_key, contract_key)
                if isOtherTableSuccss:
                    return Response({"error": 0, "detail": "Invoice Cancelled Successfully", "data": invoiceIns}, status=status.HTTP_201_CREATED)

                return Response({"error": 1, "detail": "Invalid Request, GRN_KEY might be wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

            elif invoiceCanclSucss:
                return Response({"error": 0, "detail": "Invoice Cancelled Successfully", "data": invoiceIns}, status=status.HTTP_201_CREATED)

            else:
                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 1, "detail": "Invalid action", "data": {}}, status=status.HTTP_400_BAD_REQUEST)


class ContractorTypeViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = ContractorType.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = ContractorTypeSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID, company=companyID).order_by('descr')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ContractorTypeSerializer(
                qrySet, many=True, fields=('key', 'id', 'descr'))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = ContractorTypeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)
        serializer_class = ContractorTypeSerializer(vendorTypeIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)
        vendorTypeIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ContractorTypeSerializer(
            vendorTypeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Contractor Type Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendoe Type PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor Type PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ContractorTypeSerializer(data=reqData)

        if serializer.is_valid():
            try:
                costCatIns = serializer.save()
                if costCatIns:
                    return Response({"error": 0, "detail": "Contractor Type Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Vendor Type"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContractorViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Contractor.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = ContractorSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        querySet = self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ).order_by('name')

        if request.GET.get("type", False) and UF.isNum(request.GET.get("type")):
            querySet = querySet.filter(contractortyp_key=request.GET.get("type"))

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ContractorGetSerializer(
                querySet, many=True)
            return Response(serializer.data)
        page = self.paginate_queryset(querySet)

        serializer = ContractorGetSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)

        if request.GET.get('item_type_alone', False):
            serializer_class = ContractorSerializer(
                vendorIns, fields=('itemtype',))
            return Response(serializer_class.data['itemtype'])
        else:
            serializer_class = ContractorGetSerializer(vendorIns)
            return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ContractorSerializer(
            vendorIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Contractor updated successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendor PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)
        vendorIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data

        reqData['createdby'] = UF.getCurrentSessionUser(request)

        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = clientID
        reqData['company'] = companyID

        serializer = ContractorSerializer(data=reqData)
        if serializer.is_valid():
            try:
                costCatIns = serializer.save()
                if costCatIns:
                    return Response({"error": 0, "detail": "Contractor Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print("Exception while saving contractor: ", e)
                return Response({"error": 1, "detail": "Error While Adding Vendor"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Serializer errors: ", serializer.errors)
            return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContractAgreementViewSet(viewsets.ModelViewSet):
    queryset = ContractAgreement.objects.all()
    serializer_class = ContractAgreementSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = ContractAgreementListSerializer(qrySet, many=True)
            return Response(serializer.data)

        if request.GET.get("project", False) and UF.isNum(request.GET.get("project")):
            qrySet = qrySet.filter(project_id=request.GET.get("project"))

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = ContractAgreementListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ContractAgreementListSerializer(qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"Contract agreement with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ContractAgreementGetSerializer(qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        contract_agreement_obj = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID,
            key=pk,
        )).delete()

        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])

            req_data = request.data
            req_data['id'] = ContractAgreement.nextID()
            req_data['company_id'] = companyID
            req_data['client_id'] = clientID
            updated_agreement_no = UF.getValidDocId(
                req_data['agreement_no'], "CAN", clientID)
            req_data['agreement_no'] = updated_agreement_no

            contract_agrmnt_serializer = ContractAgreementSerializer(
                data=req_data)

            if contract_agrmnt_serializer.is_valid():
                contract_agreement = contract_agrmnt_serializer.save()
                contract_agrmnt_key = contract_agreement.key

                service_desc_errors = []
                payment_schedule_errors = []

                if 'service_descriptions' in req_data and req_data['service_descriptions']:
                    for service_desc_data in req_data['service_descriptions']:
                        service_desc_data['id'] = ContractAgreementService.nextID(
                        )
                        service_desc_data['contract_agreement_id'] = contract_agrmnt_key
                        service_desc_serializer = ContractAgreementServiceSerializer(
                            data=service_desc_data)

                        if service_desc_serializer.is_valid():
                            service_desc_serializer.save()
                        else:
                            service_desc_errors.append(
                                service_desc_serializer.errors)

                if 'payment_schedules' in req_data and req_data['payment_schedules']:
                    for payment_schedule_data in req_data['payment_schedules']:
                        payment_schedule_data['id'] = ContractAgreementPaymentSchedule.nextID(
                        )
                        payment_schedule_data['contract_agreement_id'] = contract_agrmnt_key
                        payment_schedule_serializer = ContractAgreementPaymentScheduleSerializer(
                            data=payment_schedule_data)

                        if payment_schedule_serializer.is_valid():
                            payment_schedule_serializer.save()
                        else:
                            payment_schedule_errors.append(
                                payment_schedule_serializer.errors)

                if service_desc_errors or payment_schedule_errors:
                    transaction.set_rollback(True)
                    error_detail = {
                        "error": 1,
                        "detail": "Error in Service Description or Payment Schedule data",
                        "service_description_errors": service_desc_errors,
                        "payment_schedule_errors": payment_schedule_errors
                    }
                    return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"error": 1, "detail": "Error in Contract Agreement data", "data": contract_agrmnt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Contract Agreement Added Successfully", "data": contract_agrmnt_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            print("Exception occurred:", str(e))
            return Response({"error": 1, "detail": "An error occurred while creating the Contract Agreement.", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            contract_agreement = ContractAgreement.objects.get(key=pk)
        except ContractAgreement.DoesNotExist:
            return Response({"error": 1, "detail": "Contract Agreement does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID

        contract_agrmnt_serializer = ContractAgreementSerializer(
            contract_agreement, data=req_data, partial=True)

        if contract_agrmnt_serializer.is_valid():
            try:
                with transaction.atomic():
                    contract_agrmnt_serializer.save()

                    processed_service_desc_keys = []
                    processed_payment_schedule_keys = []

                    for service_desc_data in req_data.get('service_descriptions', []):
                        service_desc_key = service_desc_data.get('key')
                        if service_desc_key:
                            service_description = ContractAgreementService.objects.get(
                                pk=service_desc_key)
                            service_desc_serializer = ContractAgreementServiceSerializer(
                                instance=service_description, data=service_desc_data, partial=True)
                        else:
                            service_desc_data['contract_agreement_id'] = contract_agreement.key
                            service_desc_data['id'] = ContractAgreementService.nextID(
                            )
                            service_desc_serializer = ContractAgreementServiceSerializer(
                                data=service_desc_data)

                        if service_desc_serializer.is_valid():
                            service_desc_serializer.save()
                            processed_service_desc_keys.append(
                                service_desc_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": service_desc_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    for payment_schedule_data in req_data.get('payment_schedules', []):
                        payment_schedule_key = payment_schedule_data.get('key')
                        if payment_schedule_key:
                            payment_schedule = ContractAgreementPaymentSchedule.objects.get(
                                pk=payment_schedule_key)
                            payment_schedule_serializer = ContractAgreementPaymentScheduleSerializer(
                                instance=payment_schedule, data=payment_schedule_data, partial=True)
                        else:
                            payment_schedule_data['contract_agreement_id'] = contract_agreement.key
                            payment_schedule_data['id'] = ContractAgreementPaymentSchedule.nextID(
                            )
                            payment_schedule_serializer = ContractAgreementPaymentScheduleSerializer(
                                data=payment_schedule_data)

                        if payment_schedule_serializer.is_valid():
                            payment_schedule_serializer.save()
                            processed_payment_schedule_keys.append(
                                payment_schedule_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": payment_schedule_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    ContractAgreementService.objects.filter(contract_agreement_id=contract_agreement.key).exclude(
                        key__in=processed_service_desc_keys).delete()

                    ContractAgreementPaymentSchedule.objects.filter(contract_agreement_id=contract_agreement.key).exclude(
                        key__in=processed_payment_schedule_keys).delete()

                    return Response({"error": 0, "detail": "Contract Agreement Updated Successfully", "data": contract_agrmnt_serializer.data}, status=status.HTTP_200_OK)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": 1, "detail": "Error in Contract Agreement data", "data": contract_agrmnt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContractorInvoiceViewSet(viewsets.ModelViewSet):
    queryset = ContractorInvoice.objects.all()
    serializer_class = ContractorInvoiceSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('invoice_date')

        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        print("fromdate, todate ::", from_date, to_date)

        if from_date and to_date:
            print("inside the if statement fromdate, todate ::", from_date, to_date)
            if from_date <= to_date:
                try:
                    from_date = from_date.strip()
                    to_date = to_date.strip()
                    qrySet = qrySet.filter(invoice_date__gte=from_date, invoice_date__lte=to_date).order_by('invoice_date')
                except ValueError: 
                    return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            else :
                return Response({"error": "Invalid date values. From date has to be lower than To date"}, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = ContractorInvoiceSerializer(qrySet, many=True)
            return Response(serializer.data)
        
        print("before filtering the project qrySet ::", qrySet)

        if request.GET.get("project_id", False) and UF.isNum(request.GET.get("project_id")):
            qrySet = qrySet.filter(project_id=request.GET.get("project_id"))
        
        print("after filtering the project qrySet ::", qrySet)

        if request.GET.get("contractor_id", False) and UF.isNum(request.GET.get("contractor_id")):
            qrySet = qrySet.filter(contractor_id=request.GET.get("contractor_id"))

        print("after filtering the contractor_id qrySet ::", qrySet)

        if request.GET.get("agreement_id", False) and UF.isNum(request.GET.get("agreement_id")):
            qrySet = qrySet.filter(agreement_id=request.GET.get("agreement_id"))
        
        print("after filtering the agreement_id qrySet ::", qrySet)

        page = self.paginate_queryset(qrySet)
        total_invoice_amount = qrySet.aggregate(total=Sum('invoice_amount'))['total'] or 0 
        if page is not None:
            serializer = ContractorInvoiceSerializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data["total_invoice_amount"]=total_invoice_amount
            return paginated_response

        serializer = ContractorInvoiceSerializer(qrySet, many=True)
        return Response({
            "results" : serializer.data,
            "total_invoice_amount": total_invoice_amount
        })

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"Contractor invoice with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ContractorInvoiceSerializer(qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        try:
            contract_invoice_obj = ContractorInvoice.objects.filter(
                company_id=companyID,
                client_id=clientID,
                key=pk,
            ).first()
            if contract_invoice_obj.payment_schedule_id: 
                contract_invoice_obj.payment_schedule_id.stage_status = 'O'
                contract_invoice_obj.payment_schedule_id.save()
            contract_invoice_obj.delete()
        
        except ContractorInvoice.DoesNotExist:
            return Response({"detail":"Contractor Invoice does not exist"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            print(f"error while deleting contractor invoice: {e}")
            return Response({"detail":"Error Occured while deleting"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])

            req_data = request.data
            
            req_data['company_id'] = companyID
            req_data['client_id'] = clientID
            updated_invoice_id = UF.getValidDocId(
                req_data['invoice_id'], "CIN", clientID)
            req_data['invoice_id'] = updated_invoice_id
            if req_data['invoice_type'] == 'N':
                req_data['agreement_id'] = None
            if req_data['payment_schedule_id']:
                stage_ins = ContractAgreementPaymentSchedule.objects.filter(key=req_data['payment_schedule_id']).first()
                stage_ins.stage_status='I'
            contract_invoice_serializer = ContractorInvoiceSerializer(
                data=req_data)

            if contract_invoice_serializer.is_valid():
                if req_data['payment_schedule_id']:
                    stage_ins.save()
                contract_invoice_serializer.save()

            else:
                return Response({"error": 1, "detail": F"Error in Contractor Invoice data: {contract_invoice_serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Contractor Invoice Added Successfully", "data": contract_invoice_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            print("Exception occurred:", str(e))
            return Response({"error": 1, "detail": F"An error occurred while creating the Contract Invoice: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            contract_invoice = ContractorInvoice.objects.get(key=pk)
        except ContractorInvoice.DoesNotExist:
            return Response({"error": 1, "detail": "Contractor Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID
        if req_data['payment_schedule_id']:
            schedule_from_payload = req_data['payment_schedule_id']
            schedule_from_db = contract_invoice.payment_schedule_id
            if schedule_from_payload != schedule_from_db:
                schedule_from_db.stage_status = "O"
                try:
                    stage_ins = ContractAgreementPaymentSchedule.objects.filter(key=schedule_from_payload).first()
                    stage_ins.stage_status="I"
                except ContractAgreementPaymentSchedule.DoesNotExist:
                    return Response({"error": 1, "detail": "Contract Payment Schedule does not exists"}, status=status.HTTP_404_NOT_FOUND)
        contract_invoice_serializer = ContractorInvoiceSerializer(
            instance=contract_invoice, data=req_data, partial=True)

        if contract_invoice_serializer.is_valid():
            if req_data['payment_schedule_id']:
                schedule_from_db.save()
                stage_ins.save()
            contract_invoice_serializer.save()
            return Response({"error": 0, "detail": "Contractor Invoice Updated Successfully", "data": contract_invoice_serializer.data}, status=status.HTTP_200_OK)

        else:
            return Response({"error": 1, "detail": "Error in Contractor Invoice data", "data": contract_invoice_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContractorInvoiceAllView(APIView):

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')
        contractor_type_id = request.query_params.get('contractor_type_id')
        contractor_id = request.query_params.get('contractor_id')
        agreement_id = request.query_params.get('agreement_id')
        inhouse = request.query_params.get('inhouse')
        all_schedules = request.query_params.get('all_schedules')

        if project_id and contractor_type_id and not contractor_id and not agreement_id:
            return self.get_contractor_ids(project_id, contractor_type_id)

        elif project_id and contractor_type_id and contractor_id and not agreement_id:
            return self.get_agreement_details(project_id, contractor_type_id, contractor_id)

        elif agreement_id and project_id and not contractor_type_id and not contractor_id:
            return self.get_related_details(project_id, agreement_id)

        elif agreement_id and all_schedules and not contractor_id and not project_id and not contractor_type_id:
            return self.get_payment_schedule_details(agreement_id, all_schedules=True)
        
        elif agreement_id and not contractor_id and not project_id and not contractor_type_id:
            return self.get_payment_schedule_details(agreement_id)

        elif inhouse:
            return self.get_inhouse_invoices(request, project_id, contractor_id)

        return Response({'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def get_contractor_ids(self, project_id, contractor_type_id):
        contract_agreements = ContractAgreement.objects.filter(
            project_id=project_id,
            contractor_id__contractortyp_key=contractor_type_id
        ).select_related('contractor_id')

        inhouse_contractors = Contractor.objects.filter(
            contractortyp_key=contractor_type_id, inhouse='Y')

        seen_contractors = set()
        response_data = []

        for agreement in contract_agreements:
            contractor = agreement.contractor_id
            if contractor.key not in seen_contractors:
                seen_contractors.add(contractor.key)
                response_data.append({
                    "name": contractor.name,
                    "key": contractor.key,
                    "inhouse": contractor.inhouse
                })

        for contractor in inhouse_contractors:
            if contractor.key not in seen_contractors:
                seen_contractors.add(contractor.key)
                response_data.append({
                    "name": contractor.name,
                    "key": contractor.key,
                    "inhouse": contractor.inhouse
                })

        return Response(response_data)

    def get_agreement_details(self, project_id, contractor_type_id, contractor_id):

        agreements = ContractAgreement.objects.filter(
            project_id=project_id,
            contractor_id__contractortyp_key=contractor_type_id,
            contractor_id=contractor_id
        )

        agreements_data = []
        for agreement in agreements:
            agreement_data = {
                'key': agreement.key,
                'agreement_no': agreement.agreement_no,
                'paid_amount': agreement.paid_amount,
                'total_amount': agreement.total_amount
            }
            agreements_data.append(agreement_data)

        return Response(agreements_data)

    def get_related_details(self, project_id, agreement_id):
        invoices = ContractorInvoice.objects.filter(
            agreement_id=agreement_id,
            project_id=project_id
        ).order_by("invoice_date")
        serializer = ContractorInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def get_payment_schedule_details(self, agreement_id, all_schedules=False):
        if all_schedules:
            payment_schedules = ContractAgreementPaymentSchedule.objects.filter(
                contract_agreement_id=agreement_id)
        else:
            payment_schedules = ContractAgreementPaymentSchedule.objects.filter(
                contract_agreement_id=agreement_id, stage_status='O')

        serializer = ContractAgreementPaymentScheduleSerializer(
            payment_schedules, many=True)
        return Response(serializer.data)

    def get_inhouse_invoices(self, request, project_id, contractor_id):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        invoices = ContractorInvoice.objects.filter(
            company_id=companyID,
            client_id=clientID,
            contractor_id=contractor_id,
            project_id=project_id
        ).order_by('invoice_date')
        serializer = ContractorInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class ContractInvAllocAmtView(viewsets.ModelViewSet):
    queryset = ContractInvAllocAmt.objects.all()
    serializer_class = ContractInvAllocAmtSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        invoice_id = request.query_params.get('invoice_id')
        contractor_id = request.query_params.get('contractor_id')
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        if invoice_id:
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])

            querySet = ContractorInvoice.objects.filter(
                company_id=companyID,
                client_id=clientID,
                invoice_id=invoice_id
            ).exclude(invoice_status='P')
            print("querySet", querySet)
            if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
                serializer = PayInvoiceSerializer(querySet, many=True)
                return Response(serializer.data)

            page = self.paginate_queryset(querySet)
            if page is not None:
                serializer = PayInvoiceSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = PayInvoiceSerializer(querySet, many=True)
            return Response(serializer.data)

        elif contractor_id:
            querySet = ContractorInvoice.objects.filter(
                company_id=companyID,
                client_id=clientID,
                contractor_id=contractor_id
            ).exclude(invoice_status='P')

            if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
                serializer = PayContractorSerializer(querySet, many=True)
                return Response(serializer.data)

            page = self.paginate_queryset(querySet)
            if page is not None:
                serializer = PayContractorSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = PayContractorSerializer(querySet, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 1, "detail": "invalid request parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(
                client_id=clientID,
                key=pk
            )
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"ContractInvAllocAmt with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ContractInvAllocAmtGetSerializer(qrySet, many=False)
        return Response(serializer.data)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data_list = request.data

        errors = []
        successes = []

        for req_data in req_data_list:
            req_data['client_id'] = clientID
            serializer = ContractInvAllocAmtSerializer(data=req_data)

            if serializer.is_valid():
                serializer.save()
                successes.append(serializer.data)
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"error": 1, "detail": "Errors in ContractInvAllocAmt data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 0, "detail": "ContractInvAllocAmts Added Successfully", "data": successes}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        invoices = request.data.get('invoices', [])

        errors = []
        successes = []

        for invoice_data in invoices:
            allocated_amount_details = invoice_data.get(
                'allocated_amount_details')

            if allocated_amount_details is None:
                invoice_id = invoice_data.get('key')
                existing_alloc_objs = ContractInvAllocAmt.objects.filter(
                    invoice_id=invoice_id, client_id=clientID)
                if existing_alloc_objs.exists():
                    existing_alloc_objs.delete()
                continue

            if 'key' not in allocated_amount_details:
                first_key = next((k for k in allocated_amount_details if k.isdigit()), None)
                if first_key:
                    allocated_amount_details = allocated_amount_details[first_key]
    
            allocated_amount_key = allocated_amount_details.get('key')
            if allocated_amount_key is not None:
                try:
                    contract_inv_alloc_amt = ContractInvAllocAmt.objects.get(
                        key=allocated_amount_key, client_id=clientID)
                    action = 'updated'
                except ContractInvAllocAmt.DoesNotExist:
                    contract_inv_alloc_amt = None
                    action = 'created'
            else:
                contract_inv_alloc_amt = None
                action = 'created'

            invoice_data['client_id'] = clientID
            invoice_data['invoice_id'] = invoice_data['key']

            if contract_inv_alloc_amt:
                contract_inv_alloc_amt_serializer = ContractInvAllocAmtSerializer(
                    instance=contract_inv_alloc_amt, data=invoice_data, partial=True)
            else:
                invoice_data['allocated_amount'] = allocated_amount_details['allocated_amount']
                if invoice_data.get('allocated_amount') is not None:
                    contract_inv_alloc_amt_serializer = ContractInvAllocAmtSerializer(
                        data=invoice_data)
                else:
                    continue

            if contract_inv_alloc_amt_serializer.is_valid():
                contract_inv_alloc_amt_serializer.save()
                successes.append(
                    {"action": action, "data": contract_inv_alloc_amt_serializer.data})
            else:
                errors.append({"error": 1, "detail": f"Error in ContractInvAllocAmt data for id {allocated_amount_key}",
                              "data": contract_inv_alloc_amt_serializer.errors})

        if errors:
            return Response({"error": 1, "detail": "Errors in processing ContractInvAllocAmt data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 0, "detail": "ContractInvAllocAmts processed successfully", "data": successes}, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ContractInvAllocAmt_obj = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            key=pk,
        )).delete()

        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)


class ContractVoucherViewSet(viewsets.ModelViewSet):
    queryset = ContractVoucherHdr.objects.all()
    serializer_class = ContractVoucherHdrSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key')

        agreement_id = request.GET.get("agreement_id")
        year = request.GET.get("year")
        month = request.GET.get("month")

        if year and month:
            qrySet = qrySet.filter(
                contract_voucher_dt__year=year,
                contract_voucher_dt__month=month
            )

        if agreement_id:
            voucher_detail = ContractVoucherDtl.objects.filter(
                client_id=clientID,
                invoice_id__agreement_id=agreement_id
            )
            contract_voucher_hdr_ids = voucher_detail.values_list(
                'contract_voucher_hdr', flat=True
            )
            qrySet = qrySet.filter(
                key__in=contract_voucher_hdr_ids
            )

            from django.db.models import Sum
            voucher_agreement_sums = dict(
                voucher_detail.values('contract_voucher_hdr')
                .annotate(agreement_paid=Sum('paid_amount'))
                .values_list('contract_voucher_hdr', 'agreement_paid')
            )

            serializer = ContractVoucherHdrListSerializer(qrySet, many=True)
            data = serializer.data

            for item in data:
                hdr_id = item['key']
                if hdr_id in voucher_agreement_sums:
                    item['total_amount'] = voucher_agreement_sums[hdr_id]

            if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
                return Response(data)

            page = self.paginate_queryset(data)
            if page is not None:
                return self.get_paginated_response(page)

            return Response(data)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = ContractVoucherHdrListSerializer(qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = ContractVoucherHdrListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ContractVoucherHdrListSerializer(qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"Contract Voucher with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ContractVoucherHdrGetSerializer(qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            with transaction.atomic():
                qrySet = self.queryset.get(
                    company_id=companyID,
                    client_id=clientID,
                    key=pk
                )

                contract_voucher_hdr_key = qrySet.key
                contract_voucher_dtl = ContractVoucherDtl.objects.filter(
                    contract_voucher_hdr=contract_voucher_hdr_key)

                for voucher in contract_voucher_dtl:
                    voucher_paid_amount = voucher.paid_amount

                    try:
                        contract_invoice_obj = ContractorInvoice.objects.get(
                            key=voucher.invoice_id.key
                        )
                    except ContractorInvoice.DoesNotExist:
                        return Response(
                            {"error": f"Contractor Invoice with id {voucher.invoice_id.key} does not exist"},
                            status=status.HTTP_404_NOT_FOUND
                        )

                    invoice_paid_amount = contract_invoice_obj.paid_amount
                    balance_amount = invoice_paid_amount - voucher_paid_amount

                    contract_invoice_obj.paid_amount = balance_amount

                    if balance_amount == 0.00:
                        contract_invoice_obj.invoice_status = 'O'
                    else:
                        contract_invoice_obj.invoice_status = 'A'

                    contract_invoice_obj.save()
                    if contract_invoice_obj.agreement_id:
                        try:
                            agreement_obj = ContractAgreement.objects.get(
                                key=contract_invoice_obj.agreement_id.key
                            )
                            print('agrmnt obj', agreement_obj)
                            current_agrmnt_paid_amount = agreement_obj.paid_amount if agreement_obj.paid_amount is not None else 0.00
                            print('current_agrmnt_paid_amount', current_agrmnt_paid_amount)
                            current_agrmnt_paid_amount -= voucher_paid_amount
                            agreement_obj.paid_amount = current_agrmnt_paid_amount
                            agreement_obj.save()

                        except ContractAgreement.DoesNotExist:
                            return Response(
                                {"error": f"Contract Agreement with id {contract_invoice_obj.agreement_id.key} does not exist"},
                                status=status.HTTP_404_NOT_FOUND
                            )

                    if contract_invoice_obj.tds_amount:
                        if contract_invoice_obj.invoice_status == 'O':
                            
                            tds_entry_instance = TdsEntry.objects.filter(
                                contractor_invoice=contract_invoice_obj.key
                            ).first()

                            if tds_entry_instance:
                                month = tds_entry_instance.date.month
                                year = tds_entry_instance.date.year
                                contractor = contract_invoice_obj.contractor_id

                                tds_report_instance = TdsReport.objects.filter(
                                    contractor=contractor,
                                    date__month=month,
                                    date__year=year
                                ).first()

                                if tds_report_instance:
                                    tds_report_instance.amount -= contract_invoice_obj.tds_amount
                                    if tds_report_instance.amount <= 0.00:
                                        tds_report_instance.delete()
                                    else:
                                        tds_report_instance.save()
                                else:
                                    return Response(
                                        {"error": "TDS Report instance not found for the given month and year"},
                                        status=status.HTTP_404_NOT_FOUND
                                    )
                                tds_entry_instance.delete()
                qrySet.delete()

                return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': f"Contract Voucher with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response(
                {"error": "Delete Failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID
        voucher_no = UF.getValidDocId(
            req_data['voucher_number'], "VN", clientID)
        req_data['voucher_number'] = voucher_no
        contract_voucher_hdr_serializer = ContractVoucherHdrSerializer(
            data=req_data)

        if not contract_voucher_hdr_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Contract Voucher Hdr data", "data": contract_voucher_hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            contract_voucher_hdr = contract_voucher_hdr_serializer.save()

            agreement_allocations = {}
            invoices = req_data.get('invoices', [])
            for invoice_data in invoices:
                allocated_amount = invoice_data.get('allocated_amount')
                if allocated_amount is None:
                    return Response({"error": 1, "detail": "Allocated amount missing for an invoice"}, status=status.HTTP_400_BAD_REQUEST)

                invoice_id = invoice_data.get('key')
                if invoice_id is None:
                    return Response({"error": 1, "detail": "Invoice key missing for creating ContractVoucherDtl"}, status=status.HTTP_400_BAD_REQUEST)

                dtl_data = {
                    'contract_voucher_hdr': contract_voucher_hdr.key,
                    'invoice_id': invoice_id,
                    'paid_amount': allocated_amount,
                    'client_id': clientID
                }
                contract_voucher_dtl_serializer = ContractVoucherDtlSerializer(
                    data=dtl_data)

                if contract_voucher_dtl_serializer.is_valid():
                    contract_voucher_dtl_serializer.save()
                else:
                    transaction.set_rollback(True)
                    return Response({"error": 1, "detail": "Error in Contract Voucher Dtl data", "data": contract_voucher_dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                # Remove allocation amount details if key is provided
                allocated_amount_details = invoice_data.get(
                    'allocated_amount_details')
                if allocated_amount_details:
                    for k, v in allocated_amount_details.items():
                        if isinstance(v, dict) and 'key' in v:
                            alloc_key = v['key']
                            try:
                                alloc_amt_obj = ContractInvAllocAmt.objects.get(key=alloc_key)
                                alloc_amt_obj.delete()
                            except ContractInvAllocAmt.DoesNotExist:
                                transaction.set_rollback(True)
                                return Response(
                                    {'error': 1, "detail": f"Contract Invoice allocated amount with id {alloc_key} does not exist"},
                                    status=status.HTTP_404_NOT_FOUND
                                )
                try:
                    invoice_obj = ContractorInvoice.objects.get(key=invoice_id)

                    current_paid_amount = float(
                        invoice_obj.paid_amount) if invoice_obj.paid_amount else 0.0

                    invoice_obj.paid_amount = current_paid_amount + \
                        float(allocated_amount)

                    if float(invoice_obj.paid_amount) == float(invoice_obj.invoice_amount):
                        invoice_obj.invoice_status = 'P'
                    elif float(invoice_obj.paid_amount) < float(invoice_obj.invoice_amount):
                        invoice_obj.invoice_status = 'A'

                    if invoice_obj.agreement_id:
                        agreement_key = invoice_obj.agreement_id.key
                        agreement_allocations[agreement_key] = agreement_allocations.get(
                            agreement_key, 0
                        ) +  allocated_amount

                    invoice_obj.save()

                    if invoice_obj.tds_amount:
                        tds_entry = TdsEntry.objects.filter(contractor_invoice = invoice_obj.key)
                        if not tds_entry:
                            tds_entry_data = {
                                'date': datetime.today().date(),
                                'contractor_invoice': invoice_obj.key,
                                'invoice_type': 'C',
                                'amount': invoice_obj.tds_amount,
                                'payment_status': 'Unpaid',
                                'client': clientID,
                                'company': companyID
                            }
                            tds_entry_serializer = TdsEntrySerializer(
                                data=tds_entry_data)
                            if tds_entry_serializer.is_valid():
                                tds_entry_serializer.save()
                                tds_report_instance = TdsReport.objects.filter(
                                    contractor=req_data['contractor_id'], date__month=datetime.today(
                                    ).month,
                                    date__year=datetime.today().year
                                ).first()

                                if tds_report_instance:
                                    tds_report_instance.amount += invoice_obj.tds_amount
                                    tds_report_instance.save()
                                else:
                                    tds_report_data = {
                                        'date': datetime.today().date(),
                                        'contractor': req_data['contractor_id'],
                                        'entity_type': 'C',
                                        'amount': invoice_obj.tds_amount,
                                        'payment_status': 'Unpaid',
                                        'client': clientID,
                                        'company': companyID
                                    }
                                    tds_report_serializer = TdsReportSerializer(
                                        data=tds_report_data)
                                    if tds_report_serializer.is_valid():
                                        tds_report_serializer.save()
                                    else:
                                        transaction.set_rollback(True)
                                        return Response({'error': 1, 'detail': "Error occured while processing the tds report", 'data': tds_report_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                transaction.set_rollback(True)
                                return Response({'error': 1, 'detail': 'Error occured while saving the Tds Entry for the invoice payment', 'data': tds_entry_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                except ContractorInvoice.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({'error': 1, "detail": f"ContractorInvoice with id {invoice_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            for agreement_key, total_alloc in agreement_allocations.items():
                agreement_obj = ContractAgreement.objects.get(key=agreement_key)
                if agreement_obj.paid_amount is None:
                    agreement_obj.paid_amount = 0

                agreement_obj.paid_amount += total_alloc
                agreement_obj.save()
            return Response({"error": 0, "detail": "Contract Voucher Added Successfully", "data": contract_voucher_hdr_serializer.data}, status=status.HTTP_201_CREATED)


class ContractorPaymentAllViewSet(viewsets.ModelViewSet):
    pagination_class = Pagination10PerPage

    def list(self, request):
        pay_invoice = request.query_params.get('pay_invoice')
        pay_contractor = request.query_params.get('pay_contractor')

        if pay_invoice:
            return self.get_pay_invoice_details(request)

        elif pay_contractor:
            return self.get_pay_contractor_details(request)

        return Response({'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def get_pay_invoice_details(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        querySet = ContractorInvoice.objects.filter(
            company_id=companyID,
            client_id=clientID
        ).exclude(invoice_status='P')

        # print('queryset of contractorinvoice ::', querySet)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = PayInvoiceSerializer(querySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(querySet)
        if page is not None:
            serializer = PayInvoiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PayInvoiceSerializer(querySet, many=True)
        return Response(serializer.data)

    def format_aggregated_contractor_results(self, data):
        results = []
        for item in data:
            results.append({
                "key": item["contractor_id__key"],
                "pending_amount": float(item["pending_amount"]),
                "allocated_amount": float(item["allocated_amount"]) if item["allocated_amount"] is not None else None,
                "contractor_details": {
                    "key": item["contractor_id__key"],
                    "name": item["contractor_id__name"],
                    "type": {
                        "key": item["contractor_id__contractortyp_key__key"],
                        "descr": item["contractor_id__contractortyp_key__descr"]
                    } if item["contractor_id__contractortyp_key__key"] else None
                }
            })
        return results

    def get_pay_contractor_details(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        aggregated_qs = ContractorInvoice.objects.filter(
            company_id=companyID,
            client_id=clientID
        ).exclude(invoice_status='P').values(
            'contractor_id__key',
            'contractor_id__name',
            'contractor_id__contractortyp_key__key',
            'contractor_id__contractortyp_key__descr'
        ).annotate(
            pending_amount=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F('invoice_amount') - Coalesce(F('paid_amount'), Value(0), output_field=DecimalField()),
                        output_field=DecimalField()
                    )
                ),
                Value(0),
                output_field=DecimalField()
            ),
            allocated_amount=Coalesce(Sum('contractinvallocamt__allocated_amount'), None, output_field=DecimalField())
        ).order_by('contractor_id__name')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            return Response(self.format_aggregated_contractor_results(aggregated_qs))

        page = self.paginate_queryset(aggregated_qs)
        if page is not None:
            return self.get_paginated_response(self.format_aggregated_contractor_results(page))

        return Response(self.format_aggregated_contractor_results(aggregated_qs))

