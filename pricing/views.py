from django.db import transaction
from .models import (Docid, Docstatus,
                     Goodsreceiptnote, GoodsreceiptnoteItems,
                     StockLedger, StockQoh, StockSummary,
                     Itembatch, ItembatchLedger,
                     Purchasetemplate, PurchasetemplateItems,
                     Purchaseorder, PurchaseorderItems,
                     Vendorinvoice, VendorInvoiceImage, VendorinvoiceItems,
                     Payment, Paymentalloc, Modeofpay)

from .serializers import (DocIdSerializer, DocStatusSerializer,
                          GoodsReceiptNoteSerializer, GoodsReceiptNoteItemsSerializer,
                          StockLedgerSerializer, StockQohSerializer, StockSummarySerializer,
                          ItemBatchSerializer, ItemBatchLedgerSerializer,
                          PurchaseTemplateSerializer, PurchaseTemplateItemsSerializer,
                          PurchaseOrderSerializer, PurchaseOrderItemsSerializer,
                          VendorInvoiceSerializer, VendorInvoiceImageSerializer, VendorInvoiceItemsSerializer,
                          PaymentSerializer, PaymentAllocSerializer, ModeofpaySerializer)

from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from datetime import datetime
from buildiq.utils import UtilFunctions
from buildiq.pagenation_configs import Pagination10PerPage
from django.db.models import Q
from vendor.models import Vendor, Vendortype
from django.db.models import Sum
import io
import base64
import uuid

class DocIdViewset(viewsets.GenericViewSet):
    queryset = Docid.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = DocIdSerializer

    def list(self, request):
        page = self.paginate_queryset(self.queryset.all().order_by('-docid'))
        serializer = DocIdSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        docIDIns = get_object_or_404(self.queryset, pk=pk)
        serializer_class = DocIdSerializer(docIDIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        docIDIns = get_object_or_404(self.queryset, pk=pk)
        docIDIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        docIDIns = get_object_or_404(self.queryset, pk=pk)
        serializer = DocIdSerializer(
            docIDIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Doc ID Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Doc ID PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Doc ID PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = DocIdSerializer(data=request.data)
        if serializer.is_valid():

            try:
                docIDIns = serializer.save()
                if docIDIns:
                    return Response({"error": 0, "detail": "Doc ID Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Doc ID"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DocIdNextViewset(viewsets.ViewSet):
    def list(self, request):
        try:
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])
            docid = request.GET.get('docid', False)
            if docid:
                if Docid.objects.filter(docid=docid,client_id=clientID).exists():
                    with transaction.atomic():
                        doc = Docid.objects.get(docid=docid,client_id=clientID)
                        doc.docnumber += 1
                        nextDocNumber = doc.docnumber
                        doc.save()
                else:
                    data = {
                        "docid": docid,
                        "docname": UF.obtainDOCNameFromDOCID(docid),
                        "docnumber": 1001,
                        "client_id":clientID
                    }
                    serializer = DocIdSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"error": 1, "detail": "Unable to create new doc id", "data" :serializer.errors })
                    nextDocNumber = 1001
                    
                return Response({"next_doc_id": int(nextDocNumber)})
            return Response({"error": 1, "detail": "You need to pass docid to get next number"})
        except Exception as e:
            print(e)
            return Response({"error": 1, "detail": "Internal Server Error" })
            
    


class DocStatusViewset(viewsets.GenericViewSet):
    queryset = Docstatus.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = DocStatusSerializer

    def list(self, request):
        page = self.paginate_queryset(
            self.queryset.all().order_by('-docstatus'))
        serializer = DocStatusSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        docStatusIns = get_object_or_404(self.queryset, pk=pk)
        serializer_class = DocStatusSerializer(docStatusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        docStatusIns = get_object_or_404(self.queryset, pk=pk)
        docStatusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        docStatusIns = get_object_or_404(self.queryset, pk=pk)
        serializer = DocStatusSerializer(
            docStatusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Doc Status Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Doc Status PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Doc Status PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = DocStatusSerializer(data=request.data)
        if serializer.is_valid():

            try:
                docStatusIns = serializer.save()
                if docStatusIns:
                    return Response({"error": 0, "detail": "Doc Status Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Doc Status"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GoodsReceiptNoteViewset(viewsets.GenericViewSet):
    queryset = Goodsreceiptnote.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = GoodsReceiptNoteSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(company=companyID, client_id=clientID)
        if request.GET.get('only_grn_number', False):
            serializer = GoodsReceiptNoteSerializer(qrySet.order_by(
                '-key'), read_only=True, fields=('key', 'number',), many=True)
            return Response(serializer.data)

        elif request.GET.get('docid', False):
            page = self.paginate_queryset(
                self.queryset.filter(
                    docid=request.GET.get('docid'),
                    company=companyID,
                    client_id=clientID
                ).order_by('-key')
            )
        else:
            page = self.paginate_queryset(qrySet.order_by('-key'))

        serializer = GoodsReceiptNoteSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        goodsReceiptIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = GoodsReceiptNoteSerializer(goodsReceiptIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        goodsReceiptIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        goodsReceiptIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        goodsReceiptIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer = GoodsReceiptNoteSerializer(
            goodsReceiptIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Goods Receipt Note Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Goods Receipt Note PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Goods Receipt Note PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        reqData = request.data

        if not reqData.get('action', False):
            return Response({"error": 1, "detail": "action missing", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        CURRENT_ACTION = reqData['action'].upper()

        if not CURRENT_ACTION in ["SAVE", "SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"]:
            return Response({"error": 1, "detail": "Invalid action POST request. valid actions are SAVE,SUBMIT_WITH_SAVE,SUBMIT_WITHOUT_SAVE,CANCEL", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not reqData.get('key', False):
            return Response({"error": 1, "detail": "key is required for this process", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not Goodsreceiptnote.objects.filter(key=reqData.get('key')).exists():
            return Response({"error": 1, "detail": "Invalid key", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData.get('loctyp', False):
            return Response({"error": 1, "detail": "loctyp missing. Need any of the following one PR", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData.get('docid', False):
            return Response({"error": 1, "detail": "docid missing. Need any of the following one GR1", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData.get('docid', False) in ["GR1", "GR2", "GR3"]:
            return Response({"error": 1, "detail": "Invalid Doc ID, Valid Doc IDs are GR1", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        # SAVE PROCESS
        if CURRENT_ACTION == "SAVE":
            reqData["docstatus"] = "S"

            if reqData.get("key", False) and Goodsreceiptnote.objects.filter(key=reqData.get("key")):
                reqData.pop("number")
                grnIns, grnSuccess, returnMsg, returnData = Goodsreceiptnote.objects.grnUpdate(
                    reqData, GoodsReceiptNoteSerializer, reqData.get("key"), {})
                onSuccessMsg = "Material Purchase Modified Successfully"
            else:
                reqData["number"] = UF.getValidDocId(
                    reqData['number'], reqData.get('docid'),clientID)
                grnIns, grnSuccess, returnMsg, returnData = Goodsreceiptnote.objects.saveGRN(
                    reqData, GoodsReceiptNoteSerializer)
                onSuccessMsg = "Material Purchase Added Successfully"

            if grnSuccess:
                reqData['key'] = grnIns.get("key")
                reqData['createdby'] = UF.getCurrentSessionUser(request)
                grnItmIns, grnItmSuccess, returnMsg, returnData = Goodsreceiptnote.objects.insertGRNItems(
                    reqData, GoodsReceiptNoteItemsSerializer)
                if grnItmSuccess:
                    grnIns['grn_items'] = grnItmIns
                    return Response({"error": 0, "detail": onSuccessMsg, "data": grnIns}, status=status.HTTP_201_CREATED)

                # If invoice items failed to load delete invoice entry
                Goodsreceiptnote.objects.deleteGRNByGRNID(grnIns.get("key"))

                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITH_SAVE":
            reqData["docstatus"] = "U"
            grn_key = reqData.get('key')
            reqData.pop("number")
            grnIns, grnSuccess, returnMsg, returnData = Goodsreceiptnote.objects.submitGRN(
                reqData, grn_key, GoodsReceiptNoteSerializer)
            if grnSuccess:
                reqData['createdby'] = UF.getCurrentSessionUser(request)
                grnItemsIns, grnItemSuccess, returnMsg, returnData = Goodsreceiptnote.objects.insertGRNItems(
                    reqData, GoodsReceiptNoteItemsSerializer)
                if grnItemSuccess:

                    # OTHER TABLE UPDATES
                    reqData['current_user'] = UF.getCurrentSessionUser(request)
                    reqData['current_date'] = UF.getCurrentDateAndTime()
                    isOtherTableSuccss = Goodsreceiptnote.objects.doOtherTableUpdates(
                        GoodsReceiptNoteSerializer, reqData, CURRENT_ACTION, grn_key, grnItemsIns)
                    if isOtherTableSuccss:
                        grnIns['grn_items'] = grnItemsIns
                        return Response({"error": 0, "detail": "Material Purchase Submission Success", "data": grnIns}, status=status.HTTP_201_CREATED)
                    return Response({"error": 1, "detail": "Invalid Request. GRN_KEY might be wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITHOUT_SAVE":
            reqData["docstatus"] = "U"
            reqData.pop("number")  # prevent to change number
            grn_key = reqData.get('key')
            grnItmIns = GoodsReceiptNoteItemsSerializer(
                GoodsreceiptnoteItems.objects.filter(grn_key=grn_key), many=True).data

            reqData['current_user'] = UF.getCurrentSessionUser(request)
            reqData['current_date'] = UF.getCurrentDateAndTime()

            isOtherTableSuccss = Goodsreceiptnote.objects.doOtherTableUpdates(
                GoodsReceiptNoteSerializer, reqData, CURRENT_ACTION, grn_key, grnItmIns)
            if isOtherTableSuccss:
                grnInsSerilzr = GoodsReceiptNoteSerializer(
                    Goodsreceiptnote.objects.get(key=grn_key))
                return Response({"error": 0, "detail": "Material Purchase Submitted Successfully", "data": grnInsSerilzr.data}, status=status.HTTP_201_CREATED)
            return Response({"error": 1, "detail": "Invalid Request. GRN_KEY might be wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # CANCEL PROCESS
        if CURRENT_ACTION == "CANCEL":
            reqData["docstatus"] = "C"
            reqData.pop("number")  # prevent to change voucher number
            grn_key = reqData.get('key')
            grnIns, grnCanclSucss, returnMsg, returnData, otherTableUpdateReq = Goodsreceiptnote.objects.cancelGRN(
                grn_key, GoodsReceiptNoteSerializer)
            if grnCanclSucss and otherTableUpdateReq:
                reqData['current_user'] = UF.getCurrentSessionUser(request)
                reqData['current_date'] = UF.getCurrentDateAndTime()
                isOtherTableSuccss = Goodsreceiptnote.objects.doOtherTableUpdates(
                    GoodsReceiptNoteSerializer, reqData, CURRENT_ACTION, grn_key, grnIns['grn_items'])
                if isOtherTableSuccss:
                    return Response({"error": 0, "detail": "Material Purchase Cancelled Successfully", "data": grnIns}, status=status.HTTP_201_CREATED)

                return Response({"error": 1, "detail": "Invalid Request, key might be wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

            elif grnCanclSucss:
                return Response({"error": 0, "detail": "Material Purchase Successfully", "data": grnIns}, status=status.HTTP_201_CREATED)

            else:
                return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 1, "detail": "Invalid action", "data": {}}, status=status.HTTP_400_BAD_REQUEST)


class GoodsReceiptNoteItemsViewset(viewsets.GenericViewSet):
    queryset = GoodsreceiptnoteItems.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = GoodsReceiptNoteItemsSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('grn_key', False):
            qrySet = self.queryset.filter(
                grn_key=request.GET.get('grn_key'),
                company=companyID,
                client_id=clientID
            )
            serializer = GoodsReceiptNoteItemsSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(self.queryset.filter(
                company=companyID,
                client_id=clientID
            ).order_by('-key'))
            serializer = GoodsReceiptNoteItemsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        goodsReceiptItemsIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = GoodsReceiptNoteItemsSerializer(
            goodsReceiptItemsIns)
        return Response(serializer_class.data)

    # def delete(self, request, pk=None):
    #     goodsReceiptItemsIns = get_object_or_404(self.queryset, pk=pk)
    #     goodsReceiptItemsIns.delete()
    #     return Response("Delete Success")

    # def update(self, request, pk=None):
    #     goodsReceiptItemsIns = get_object_or_404(self.queryset, pk=pk)
    #     serializer = GoodsReceiptNoteItemsSerializer(
    #         goodsReceiptItemsIns, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         try:
    #             serializer.save()
    #             return Response({"error": 0, "detail": "Goods Receipt Note Item Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    #         except:
    #             return Response({"error": 1, "detail": "Error In Goods Receipt Note Item PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response({"error": 1, "detail": "Error In Goods Receipt Note Item PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request):

    #     serializer = GoodsReceiptNoteItemsSerializer(data=request.data)
    #     if serializer.is_valid():

    #         # try:
    #         goodsReceiptItemsIns = serializer.save()
    #         if goodsReceiptItemsIns:
    #             return Response({"error": 0, "detail": "Goods Receipt Note Item Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    #         # except:
    #         #     return Response({"error": 1, "detail": "Error While Adding Goods Receipt Note Item"}, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StockLedgersViewset(viewsets.GenericViewSet):
    queryset = StockLedger.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = StockLedgerSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        goodsReceiptItemsIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ))

        page = self.paginate_queryset(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key'))
        serializer = StockLedgerSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockLedgerIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = StockLedgerSerializer(StockLedgerIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockLedgerIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        StockLedgerIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockLedgerIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = StockLedgerSerializer(
            StockLedgerIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Stock Ledger Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Stock Ledger PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Stock Ledger PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = StockLedgerSerializer(data=request.data)
        if serializer.is_valid():

            try:
                StockLedgerIns = serializer.save()
                if StockLedgerIns:
                    return Response({"error": 0, "detail": "Stock Ledger Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Stock Ledger"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StockQohViewset(viewsets.GenericViewSet):
    queryset = StockQoh.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = StockQohSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key'))
        serializer = StockQohSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockQohIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = StockQohSerializer(StockQohIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockQohIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        StockQohIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockQohIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        serializer = StockQohSerializer(
            StockQohIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Stock QOH Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Stock QOH PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Stock QOH PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = StockQohSerializer(data=request.data)
        if serializer.is_valid():

            try:
                StockQohIns = serializer.save()
                if StockQohIns:
                    return Response({"error": 0, "detail": "Stock QOH Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Stock QOH"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class StockSummaryViewset(viewsets.GenericViewSet):
    queryset = StockSummary.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = StockSummarySerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key'))
        serializer = StockSummarySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockSummaryIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = StockSummarySerializer(StockSummaryIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockSummaryIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        StockSummaryIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        StockSummaryIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = StockSummarySerializer(
            StockSummaryIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Stock Summary Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Stock Summary PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Stock Summary PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = StockSummarySerializer(data=request.data)
        if serializer.is_valid():

            try:
                StockSummaryIns = serializer.save()
                if StockSummaryIns:
                    return Response({"error": 0, "detail": "Stock Summary Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Stock Summary"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemBatchViewset(viewsets.GenericViewSet):
    queryset = Itembatch.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ItemBatchSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key'))
        serializer = ItemBatchSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ItemBatchIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = ItemBatchSerializer(ItemBatchIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ItemBatchIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        ItemBatchIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ItemBatchIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        serializer = ItemBatchSerializer(
            ItemBatchIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Item Batch Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Item Batch PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Item Batch PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = ItemBatchSerializer(data=request.data)
        if serializer.is_valid():

            try:
                ItemBatchIns = serializer.save()
                if ItemBatchIns:
                    return Response({"error": 0, "detail": "Item Batch Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Item Batch"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemBatchLedgerViewset(viewsets.GenericViewSet):
    queryset = ItembatchLedger.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ItemBatchLedgerSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key'))
        serializer = ItemBatchLedgerSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        ItemBatchLedgerIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = ItemBatchLedgerSerializer(ItemBatchLedgerIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        ItemBatchLedgerIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        ItemBatchLedgerIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        ItemBatchLedgerIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = ItemBatchLedgerSerializer(
            ItemBatchLedgerIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Item Batch Ledger Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Item Batch Ledger PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Item Batch Ledger PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = ItemBatchLedgerSerializer(data=request.data)
        if serializer.is_valid():

            try:
                ItemBatchLedgerIns = serializer.save()
                if ItemBatchLedgerIns:
                    return Response({"error": 0, "detail": "Item Batch Ledger Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Item Batch Ledger"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseTemplateViewset(viewsets.GenericViewSet):
    queryset = Purchasetemplate.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = PurchaseTemplateSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get("item_type", False):
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID,
                itemtyp_key=request.GET.get("item_type")
            )
            serializer = PurchaseTemplateSerializer(qrySet, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )
            page = self.paginate_queryset(qrySet.order_by('-key'))
            serializer = PurchaseTemplateSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purchaseTemplateIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = PurchaseTemplateSerializer(purchaseTemplateIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purchaseTemplateIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        purchaseTemplateIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purchaseTemplateIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')
        serializer = PurchaseTemplateSerializer(
            purchaseTemplateIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Purchase Template Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Purchase Template PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Purchase Template PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        reqData = request.data
        reqData["number"] = UF.getValidDocId(
            reqData['number'], reqData.get('docid'),clientID)
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = PurchaseTemplateSerializer(data=reqData)
        if serializer.is_valid():

            try:
                purchaseTemplateIns = serializer.save()
                if purchaseTemplateIns:
                    return Response({"error": 0, "detail": "Purchase Template Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Purchase Template"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseTemplateAllViewset(viewsets.ViewSet):
    queryset = Purchasetemplate.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = PurchaseTemplateSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            inactive='N',
            company_id=companyID,
            client_id=clientID
        )

        if request.GET.get("item_type", False):
            qrySet = qrySet.filter(itemtyp_key=request.GET.get("item_type"))

        serialisedData = PurchaseTemplateSerializer(
            qrySet, many=True, read_only=True).data
        return Response(serialisedData)


class PurchaseTemplateItemsViewset(viewsets.ViewSet):
    queryset = PurchasetemplateItems.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = PurchaseTemplateItemsSerializer

    def list(self, request):
        # page = self.paginate_queryset(self.queryset.all().order_by('-key'))
        # serializer = PurchaseTemplateItemsSerializer(page, many=True)
        # return self.get_paginated_response(serializer.data)
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company=companyID,
            client_id=clientID
        )
        if request.GET.get('p_template_id', False):
            qrySet = qrySet.filter(
                purtmpl_key=request.GET.get('p_template_id'))
        serializer = PurchaseTemplateItemsSerializer(
            qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purchaseTemplateItemsIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = PurchaseTemplateItemsSerializer(
            purchaseTemplateItemsIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        for items in request.data.get('items', []):
            purchaseTemplateItemsIns = get_object_or_404(
                self.queryset, pk=items.get('key'))
            purchaseTemplateItemsIns.delete()
        return Response("Delete Success")

    # def update(self, request, pk=None):
    #     purchaseTemplateItemsIns = get_object_or_404(self.queryset, pk=pk)
    #     UF = UtilFunctions()
    #     reqData = request.data
    #     reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
    #     reqData['lastmodifieddttm'] = datetime.today().strftime(
    #         '%Y-%m-%d %H:%M:%S')
    #     serializer = PurchaseTemplateItemsSerializer(
    #         purchaseTemplateItemsIns, data=reqData, partial=True)
    #     if serializer.is_valid():
    #         try:
    #             serializer.save()
    #             return Response({"error": 0, "detail": "Purchase Template Item Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    #         except:
    #             return Response({"error": 1, "detail": "Error In Purchase Template Item PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response({"error": 1, "detail": "Error In Purchase Template Item PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data

        purchaseTmpltId = reqData.get("p_template_id", False)
        company = reqData.get("company", False)
        client_id = reqData.get("client_id", False)
        user = UF.getCurrentSessionUser(request)
        # PurchasetemplateItems.objects.filter(
        #     purtmpl_key=purchaseTmpltId).delete()
        if purchaseTmpltId and company and client_id:
            insertedData = []
            for items in reqData.get('items', []):
                items['purtmpl_key'] = purchaseTmpltId
                items['company'] = company
                items['client_id'] = client_id
                items['createdby'] = user

                if items.get('key', False) and not items.get('key') == "":  # existing item
                    serializer = PurchaseTemplateItemsSerializer(
                        PurchasetemplateItems.objects.get(
                            key=items.get('key')),
                        data=items,
                        partial=True
                    )
                else:
                    serializer = PurchaseTemplateItemsSerializer(data=items)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"error": 1, "detail": "Error While Adding Purchase Template Items"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": 0, "detail": "Purchase template Items Modified Successfully", "data": insertedData}, status=status.HTTP_201_CREATED)

        else:
            return Response({"error": 1, "detail": "purchase template number (or) company (or) client_id is missing"}, status=status.HTTP_400_BAD_REQUEST)

        # UF = UtilFunctions()
        # reqData = request.data
        # reqData['createdby'] = UF.getCurrentSessionUser(request)
        # serializer = PurchaseTemplateItemsSerializer(data=reqData)
        # if serializer.is_valid():

        #     try:
        #         purchaseTemplateItemsIns = serializer.save()
        #         if purchaseTemplateItemsIns:
        #             return Response({"error": 0, "detail": "Purchase Template Item Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        #     except:
        #         return Response({"error": 1, "detail": "Error While Adding Purchase Template Item"}, status=status.HTTP_400_BAD_REQUEST)
        # return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderViewset(viewsets.GenericViewSet):
    queryset = Purchaseorder.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = PurchaseOrderSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        querySet = self.queryset.filter(
            company=companyID,
            client_id=clientID
        ).order_by('-key')
        
        if request.GET.get('vendor', False):
            querySet = querySet.filter(vend_key=request.GET.get('vendor'))
        
        if request.GET.get('project', False):
            querySet = querySet.filter(proj_key=request.GET.get('project'))
            
        if request.GET.get('status', False):
            querySet = querySet.filter(status=request.GET.get('status'))

        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if from_date and to_date:
            if from_date <= to_date:
                try:
                    querySet = querySet.filter(date__gte=from_date, date__lte=to_date)
                except ValueError:
                    return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({"error": "Invalid date values. From date has to be lower than To date"}, status=status.HTTP_400_BAD_REQUEST)

        
        if(request.GET.get('without_pagination', False)):
            serializer = PurchaseOrderSerializer(querySet, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            page = self.paginate_queryset(querySet)
            serializer = PurchaseOrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)      

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        purchaseOrderIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = PurchaseOrderSerializer(purchaseOrderIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        purchaseOrderIns = get_object_or_404(self.queryset, pk=pk)
        purchaseOrderIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purchaseOrderIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')
        serializer = PurchaseOrderSerializer(
            purchaseOrderIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                success = 0
                handledKeys=[]
                
                for item in reqData.get('items',[]):
                    if item.get('key', False) and PurchaseorderItems.objects.filter(pk=item.get('key')).exists():
                        # old item
                        print("Purchase Order Items key found :: Update Required")
                        item['lastmodifiedby'] = UF.getCurrentSessionUser(request)
                        item['lastmodifieddttm'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                        purchaseOrderItemsIns = PurchaseorderItems.objects.get(pk=item.get('key'))
                        ItemSerializer = PurchaseOrderItemsSerializer(purchaseOrderItemsIns, data=item, partial=True)
                    else:
                        # new item
                        print("Purchase Order Items key Not found :: Insert Required")
                        item['po_key'] = pk
                        item['createdby'] = reqData['createdby']
                        item['client_id'] = clientID
                        item['company'] = companyID
                        ItemSerializer = PurchaseOrderItemsSerializer(data=item)
                        
                    if ItemSerializer.is_valid():
                        try:
                            ItemSerializer.save()
                            print("Insert or Update Success!!!", ItemSerializer.data['key'])
                            handledKeys.append(ItemSerializer.data['key'])
                            success += 1
                        except Exception as e:
                            print(e)
                            return Response({"error": 1, "detail": "Error While Updating Purchase Order Items"}, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({"error": 1,"detail": "Error in API request", "data": ItemSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                if success == len(reqData.get('items',[])):
                    print("Processed Purchase Order Item Keys :: ",handledKeys, " Delete Remaining" )
                    # delete removed items
                    PurchaseorderItems.objects.filter(po_key=pk).exclude(key__in=handledKeys).delete()
                    return Response({"error": 0, "detail": "Purchase Order Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": 1, "detail": "Error In Purchase Order Item Updated"}, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                print(e)
                return Response({"error": 1, "detail": "Error In Purchase Order PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Purchase Order PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        reqData['client_id'] = clientID
        reqData['company'] = companyID
        reqData['status']= "O"
        
        serializer = PurchaseOrderSerializer(data=reqData)
        if serializer.is_valid():
            try:
                vendorInvoiceIns = serializer.save()
                poKey = vendorInvoiceIns.key
                success=0
                for item in reqData.get('items',[]):
                    item['po_key'] = poKey
                    item['createdby'] = reqData['createdby']
                    item['client_id'] = clientID
                    item['company'] = companyID
                    itemSerializer = PurchaseOrderItemsSerializer(data=item)
                    if itemSerializer.is_valid():
                        try:
                            itemSerializer.save()
                            success += 1
                        except:
                            try:
                                Purchaseorder.objects.get(pk=poKey).delete()
                                PurchaseorderItems.objects.get(po_key=poKey).delete()
                                return Response({"error": 1, "detail": "Error While Adding Purchase Order Items"}, status=status.HTTP_400_BAD_REQUEST)
                            except:
                                return Response({"error": 1, "detail": "Error While Deleting Purchase Order Items during rollback"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        try:
                            Purchaseorder.objects.get(pk=poKey).delete()
                            PurchaseorderItems.objects.get(po_key=poKey).delete()
                            return Response({"error": 1,"detail": "Error in API request", "data": itemSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                        except:
                            return Response({"error": 1, "detail": "Error While Deleting Purchase Order Items during rollback"}, status=status.HTTP_400_BAD_REQUEST)
                
                if success == len(reqData.get('items',[])):
                    UF.incrementDocId("PO",clientID)
                    return Response({"error": 0, "detail": "Purchase Order Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    try:
                        Purchaseorder.objects.get(pk=poKey).delete()
                        PurchaseorderItems.objects.get(po_key=poKey).delete()
                        return Response({"error": 1,"detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    except:
                        return Response({"error": 1, "detail": "Error While Deleting Purchase Order Items during rollback"}, status=status.HTTP_400_BAD_REQUEST) 
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Purchase Order", "exception": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1,"detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderItemsViewset(viewsets.ViewSet):
    queryset = PurchaseorderItems.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = PurchaseOrderItemsSerializer

    def list(self, request):
        # page = self.paginate_queryset(self.queryset.all().order_by('-key'))
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company=companyID,
            client_id=clientID
        )
        if request.GET.get('p_order_id', False):
            qrySet = qrySet.filter(po_key=request.GET.get('p_order_id'))
        serializer = PurchaseOrderItemsSerializer(
            qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purchaseOrderItemsIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = PurchaseOrderItemsSerializer(purchaseOrderItemsIns)
        return Response(serializer_class.data)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        purchaseOrderId = reqData.get("purchase_order_id", False)
        
        if not Purchaseorder.objects.filter(pk=purchaseOrderId).exists():
            return Response({"error": 1, "detail": "Invalid Purchase Order Id"}, status=status.HTTP_400_BAD_REQUEST)
            
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        
        user = UF.getCurrentSessionUser(request)
        PurchaseorderItems.objects.filter(po_key=purchaseOrderId).delete()
        success=0
        
        for item in reqData.get('items',[]):
            item['po_key'] = purchaseOrderId
            item['createdby'] = user
            item['client_id'] = clientID
            item['company'] = companyID
            itemSerializer = PurchaseOrderItemsSerializer(data=item)
            if itemSerializer.is_valid():
                try:
                    itemSerializer.save()
                    success += 1
                except:
                    try:
                        PurchaseorderItems.objects.get(po_key=purchaseOrderId).delete()
                        return Response({"error": 1, "detail": "Error While Adding Purchase Order Items"}, status=status.HTTP_400_BAD_REQUEST)
                    except:
                        return Response({"error": 1, "detail": "Error While Deleting Purchase Order Items during rollback"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    PurchaseorderItems.objects.get(po_key=purchaseOrderId).delete()
                    return Response({"error": 1,"detail": "Error in API request", "data": itemSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"error": 1, "detail": "Error While Deleting Purchase Order Items during rollback"}, status=status.HTTP_400_BAD_REQUEST)

        if success == len(reqData.get('items',[])):
            purchaseOrderIns = Purchaseorder.objects.get(pk=purchaseOrderId)
            return Response({"error": 0, "detail": "Purchase Order Item Added Successfully", "data":PurchaseOrderSerializer(purchaseOrderIns).data}, status=status.HTTP_201_CREATED)
        else:
            try:
                PurchaseorderItems.objects.get(po_key=PurchaseorderItems).delete()
                return Response({"error": 1,"detail": "Error in API request", "data": "Unable to save purchase order items"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": 1, "detail": "Error While Deleting Purchase Order Items during rollback"}, status=status.HTTP_400_BAD_REQUEST) 
        # reqData['createdby'] = UF.getCurrentSessionUser(request)
        # serializer = PurchaseOrderItemsSerializer(data=reqData)
        # if serializer.is_valid():

        #     try:
        #         purchaseOrderItemsIns = serializer.save()
        #         if purchaseOrderItemsIns:
        #             return Response({"error": 0, "detail": "Purchase Order Items Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        #     except:
        #         return Response({"error": 1, "detail": "Error While Adding Purchase Order Items"}, status=status.HTTP_400_BAD_REQUEST)
        # return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorInvoiceViewset(viewsets.GenericViewSet):
    queryset = Vendorinvoice.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = VendorInvoiceSerializer
    
    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        querySet = self.queryset.filter( company=companyID, client_id=clientID ).order_by('-key')
         
        if request.GET.get('vendor', False):
            querySet = querySet.filter(
                vend_key=request.GET.get('vendor'),
            )
        
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        status = request.GET.get('status')

        if from_date and to_date:
            if from_date <= to_date:
                try:
                    from_date = from_date.strip()
                    to_date = to_date.strip()
                    querySet = querySet.filter(invoicedate__gte=from_date, invoicedate__lte=to_date).order_by('invoicedate', 'key')
                except ValueError:
                    return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({"error": "Invalid date values. From date has to be lower than To date"}, status=status.HTTP_400_BAD_REQUEST)

        if status:
            status_list = status.split(',')
            querySet = querySet.filter(invoice_status__in=status_list)

        if request.GET.get('project', False):
            querySet = querySet.filter(
                proj_key=request.GET.get('project'),
            )

        if request.GET.get('item_type', False):
            querySet = querySet.filter(
                po_key__item_type_key=request.GET.get('item_type'),
            )

        total_netamt = querySet.aggregate(total=Sum('netamt'))['total'] or 0

        if(request.GET.get('without_pagination', False)):
            serializer = VendorInvoiceSerializer(querySet, many=True)
            return Response({
            "results": serializer.data,
            "total_netamt": total_netamt
            })
        
        else:
            page = self.paginate_queryset(querySet)
            serializer = VendorInvoiceSerializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data['total_netamt'] = total_netamt

            return paginated_response
    
    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        reqData['client_id'] = clientID
        reqData['company'] = companyID
        reqData['balamt'] = reqData.get('netamt', 0)

        images = reqData.pop("images", [])

        try:
            with transaction.atomic():
                vendor_invoice_serializer = VendorInvoiceSerializer(data=reqData)
                if not vendor_invoice_serializer.is_valid():
                    return Response(
                        {
                            "error": 1,
                            "detail": f"Error in Vendor Invoice data: {vendor_invoice_serializer.errors}",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                vendor_invoice = vendor_invoice_serializer.save()

                if reqData.get("po_key") and reqData.get("method") == "FromPO":
                    po = Purchaseorder.objects.filter(pk=reqData.get("po_key")).first()
                    if po:
                        po.status = "I"
                        po.lastmodifiedby = reqData['createdby']
                        po.lastmodifieddttm = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                        po.save()

                elif reqData.get("method") == "DirectWithPO":
                    reqData['status'] = "I"
                    reqData['date'] = reqData['invoicedate']
                    reqData['netamt'] = reqData['invamt']

                    purchase_order_serializer = PurchaseOrderSerializer(data=reqData)
                    if not purchase_order_serializer.is_valid():
                        return Response(
                            {
                                "error": 1,
                                "detail": f"Error in Purchase Order data: {purchase_order_serializer.errors}",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    po_instance = purchase_order_serializer.save()

                    item_errors = []
                    for item in reqData['items']:
                        item.update({
                            "po_key": po_instance.key,
                            "createdby": reqData['createdby'],
                            "client_id": clientID,
                            "company": companyID
                        })

                        item_serializer = PurchaseOrderItemsSerializer(data=item)
                        if item_serializer.is_valid():
                            item_serializer.save()
                        else:
                            item_errors.append(item_serializer.errors)

                    if item_errors:
                        return Response(
                            {
                                "error": 1,
                                "detail": "Error while saving Purchase Order items",
                                "errors": item_errors,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    vendor_invoice.po_key = po_instance
                    vendor_invoice.save()

                if images:
                    folder_path = UF.create_s3_folder_structure(
                        clientID, companyID, reqData.get("proj_key"), invoice=True
                    )

                    image_objects = []
                    for img in images:
                        try:
                            header, base64_data = img["image_url"].split(",", 1)
                            decoded = base64.b64decode(base64_data)
                            file_like = io.BytesIO(decoded)

                            filename = f"{uuid.uuid4()}.jpg"
                            s3_path = f"{folder_path}/vendor_invoices/{filename}"

                            file_url = UF.upload_file_to_s3(s3_path, file_like)
                            if not file_url:
                                raise Exception("S3 upload failed")

                            image_objects.append(
                                VendorInvoiceImage(
                                    vendor_invoice=vendor_invoice,
                                    image_url=file_url,
                                    client_id=clientID,
                                    company_id=companyID,
                                    createdby=reqData['createdby'],
                                )
                            )

                        except Exception as e:
                            raise Exception(f"Invalid invoice image: {str(e)}")

                    VendorInvoiceImage.objects.bulk_create(image_objects)

                UF.incrementDocId("VIN", clientID)
                if reqData.get("method") == "DirectWithPO":
                    UF.incrementDocId("PO", clientID)

                return Response(
                    {
                        "error": 0,
                        "detail": "Vendor Invoice added successfully.",
                        "data": vendor_invoice_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            print("Exception occurred:", str(e))
            return Response(
                {
                    "error": 1,
                    "detail": f"An error occurred while creating the Vendor Invoice: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorInvoiceIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = VendorInvoiceSerializer(vendorInvoiceIns)
        return Response(serializer_class.data)
    
    @transaction.atomic
    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendor_invoice = get_object_or_404(
            self.queryset.filter(company=companyID, client_id=clientID),
            pk=pk
        )

        invoice_images = VendorInvoiceImage.objects.filter(vendor_invoice=vendor_invoice)

        for img in invoice_images:
            UF.delete_file_from_s3(img.image_url)

        if vendor_invoice.po_key and vendor_invoice.method == "FromPO":
            purchaseInvoiceKey = vendor_invoice.po_key.key
            if Purchaseorder.objects.filter(pk=purchaseInvoiceKey).exists():
                po = Purchaseorder.objects.get(pk=purchaseInvoiceKey)
                po.status = "O"
                po.lastmodifiedby = UF.getCurrentSessionUser(request)
                po.lastmodifieddttm = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                po.save()

        elif vendor_invoice.po_key and vendor_invoice.method == "DirectWithPO":
            po_key = vendor_invoice.po_key.key
            if Purchaseorder.objects.filter(pk=po_key).exists():
                po = Purchaseorder.objects.get(pk=po_key)
                PurchaseorderItems.objects.filter(po_key=po_key).delete()
                po.delete()

        vendor_invoice.delete()

        return Response(
            {"error": 0, "detail": "Vendor Invoice deleted successfully"},
            status=status.HTTP_200_OK
        )

    
    @transaction.atomic
    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendor_invoice = get_object_or_404(
            self.queryset.filter(client_id=clientID, company=companyID),
            pk=pk
        )

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        images = reqData.pop("images", [])

        processed_po_item_keys = []

        if reqData.get('method') == "DirectWithPO":
            reqData['purchase_order']['netamt'] = reqData['invamt']
            reqData['purchase_order']['date'] = reqData['invoicedate']
            reqData['balamt'] = reqData['netamt']

            po_ins = Purchaseorder.objects.get(key=reqData['purchase_order']['key'])
            po_serializer = PurchaseOrderSerializer(
                po_ins,
                data=reqData['purchase_order'],
                partial=True
            )

            if po_serializer.is_valid():
                po_serializer.save()
            else:
                return Response(
                    {"error": 1, "detail": "Error occurred while updating the PO", "data": po_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            for item in reqData.get('items', []):
                key = item.get('key')

                if key:
                    po_item_ins = PurchaseorderItems.objects.get(key=key)
                    item_serializer = PurchaseOrderItemsSerializer(po_item_ins, data=item, partial=True)
                else:
                    item.update({
                        "po_key": reqData['purchase_order']['key'],
                        "company": companyID,
                        "client_id": clientID
                    })
                    item_serializer = PurchaseOrderItemsSerializer(data=item)

                if item_serializer.is_valid():
                    item_serializer.save()
                    processed_po_item_keys.append(item_serializer.instance.key)
                else:
                    return Response(
                        {"error": 1, "detail": "Error occurred while saving PO Items", "data": item_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            PurchaseorderItems.objects.filter(
                po_key=reqData['purchase_order']['key']
            ).exclude(key__in=processed_po_item_keys).delete()

        serializer = VendorInvoiceSerializer(
            vendor_invoice,
            data=reqData,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                {"error": 1, "detail": "Error in Vendor Invoice PUT Request", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        existing_images_qs = VendorInvoiceImage.objects.filter(vendor_invoice=vendor_invoice)
        existing_image_urls_db = set(existing_images_qs.values_list("image_url", flat=True))

        payload_existing_urls = set()
        new_base64_images = []

        for img in images:
            img_url = img.get("image_url")
            if img_url and img_url.startswith("data:image"):
                new_base64_images.append(img_url)
            elif img_url:
                payload_existing_urls.add(img_url)

        images_to_delete = existing_image_urls_db - payload_existing_urls

        for img_obj in existing_images_qs.filter(image_url__in=images_to_delete):
            UF.delete_file_from_s3(img_obj.image_url)
            img_obj.delete()

        if new_base64_images:
            folder_path = UF.create_s3_folder_structure(
                clientID, companyID, reqData.get("proj_key"), invoice=True
            )

            image_objects = []

            for base64_img in new_base64_images:
                try:
                    header, base64_data = base64_img.split(",", 1)
                    decoded = base64.b64decode(base64_data)
                    file_like = io.BytesIO(decoded)

                    filename = f"{uuid.uuid4()}.jpg"
                    s3_path = f"{folder_path}/vendor_invoices/{filename}"

                    file_url = UF.upload_file_to_s3(s3_path, file_like)
                    if not file_url:
                        raise Exception("S3 upload failed")

                    image_objects.append(
                        VendorInvoiceImage(
                            vendor_invoice=vendor_invoice,
                            image_url=file_url,
                            client_id=clientID,
                            company_id=companyID,
                            createdby=reqData['lastmodifiedby'],
                        )
                    )

                except Exception as e:
                    raise Exception(f"Invalid invoice image: {str(e)}")

            VendorInvoiceImage.objects.bulk_create(image_objects)

        return Response(
            {
                "error": 0,
                "detail": "Vendor Invoice Updated Successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

class VendorinvoiceItemsViewset(viewsets.ViewSet):
    queryset = VendorinvoiceItems.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = VendorInvoiceItemsSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company=companyID,
            client_id=clientID
        )
        if request.GET.get('invoice_id', False):
            qrySet = qrySet.filter(vendinv_key=request.GET.get('invoice_id'))
        serializer = VendorInvoiceItemsSerializer(
            qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        VendorinvoiceItemsIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = VendorInvoiceItemsSerializer(VendorinvoiceItemsIns)
        return Response(serializer_class.data)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data

        if reqData.get("action", False):
            return Response({"error": 1, "detail": "Action param Missing", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        invoiceId = reqData.get("invoice_id", False)
        company = reqData.get("company", False)
        client_id = reqData.get("client_id", False)
        user = UF.getCurrentSessionUser(request)

        VendorinvoiceItems.objects.filter(vendinv_key=invoiceId).delete()

        if invoiceId and company and client_id:
            insertedData = []
            for items in reqData.get('items', []):
                items['vendinv_key'] = invoiceId
                items['company'] = company
                items['client_id'] = client_id
                items['createdby'] = user
                serializer = VendorInvoiceItemsSerializer(data=items)
                try:
                    if serializer.is_valid():
                        serializer.save()
                        insertedData.append(serializer.data)
                    else:
                        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"error": 1, "detail": "Error While Adding Invoice Items"}, status=status.HTTP_400_BAD_REQUEST)

            if len(insertedData) == reqData.get('items', []):
                # # OTHER TABLE UPDATES
                # reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
                # reqData['lastmodifieddttm'] = datetime.today().strftime(
                #     '%Y-%m-%d %H:%M:%S')

                # otherTableUpdateSuccess, returnMsg, returnData = Vendorinvoice.objects.doOtherTableUpdates(
                #     VendorInvoiceSerializer, reqData, reqData.get("action").upper(), invoiceId)
                # if not otherTableUpdateSuccess:
                #     return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)
                # else:
                #     return Response({"error": 0, "detail": returnMsg, "data": insertedData}, status=status.HTTP_201_CREATED)
                return Response({"error": 0, "detail": "Invoice Items Modified Successfully", "data": insertedData}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": 1, "detail": "Error While Adding Invoice Items"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": 1, "detail": "Invoice number (or) company (or) client_id is missing"}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewset(viewsets.GenericViewSet):
    queryset = Payment.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = PaymentSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('vendor_type', False):
            VndTypeIds = []
            if request.GET.get('vendor_type').upper() == "CONTRACTOR":
                VndTypeIds = Vendortype.objects.filter(
                    contractor="Y",
                    company=companyID,
                    client_id=clientID
                ).values_list('key', flat=True)
            else:
                VndTypeIds = Vendortype.objects.filter(
                    Q(contractor="N") | Q(contractor__isnull=True),
                    company=companyID,
                    client_id=clientID
                ).values_list('key', flat=True)

            validVendors = Vendor.objects.filter(
                inactive='N',
                vendtyp_key__in=VndTypeIds,
                company=companyID,
                client_id=clientID
            ).values_list('key', flat=True)

            serializer = PaymentSerializer(self.queryset.filter(
                vend_key__in=validVendors,
                company=companyID,
                client_id=clientID
            ).order_by('-key'), many=True)
            return Response(serializer.data)
        else:
            print(request.GET)
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            ).order_by('-key')
            
            if request.GET.get('vendor', False):
                qrySet = qrySet.filter(vend_key=request.GET.get('vendor'))
                
            if request.GET.get('paymentfrom', False):
                fromDate = datetime.strptime(request.GET.get('paymentfrom'), "%d-%m-%Y")
                qrySet = qrySet.filter(date__gte=fromDate)
                
            if request.GET.get('paymentto', False):
                toDate = datetime.strptime(request.GET.get('paymentto'), "%d-%m-%Y")
                qrySet = qrySet.filter(date__lte=toDate)
            
            page = self.paginate_queryset(qrySet)
            serializer = PaymentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        paymentIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = PaymentSerializer(paymentIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        paymentIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        paymentIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        paymentIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')
        serializer = PaymentSerializer(
            paymentIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Payment Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Payment PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Payment PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        docid = request.GET.get('docid', False)
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        if not reqData.get('action', False):
            return Response({"error": 1, "detail": "action missing", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if not reqData['action'].upper() in ["SAVE", "SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"]:
            return Response({"error": 1, "detail": "Invalid action POST request. valid actions are SAVE,SUBMIT_WITH_SAVE,SUBMIT_WITHOUT_SAVE,CANCEL", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        CURRENT_ACTION = reqData['action'].upper()

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not reqData.get('key', False):
            return Response({"error": 1, "detail": "key (Payment Key) is required for this process", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        if CURRENT_ACTION in ["SUBMIT_WITH_SAVE", "SUBMIT_WITHOUT_SAVE", "CANCEL"] and not Payment.objects.filter(key=reqData.get('key')).exists():
            return Response({"error": 1, "detail": "Invalid Payment key", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        # SAVE PROCESS
        if CURRENT_ACTION == "SAVE":
            reqData["docstatus"] = "S"
            if reqData.get("key", False) and Payment.objects.filter(key=reqData.get("key")):
                reqData.pop("number")
                reqData.pop("docid")
                payIns, paySuccess, returnMsg, returnData = Payment.objects.updatePayment(
                    reqData,
                    PaymentSerializer,
                    reqData.get("key"),
                    {}
                )
                onSuccessMsg = "Payment Details Modified Successfully"
            else:
                reqData["number"] = UF.getValidDocId(reqData['number'], "PYV",clientID)
                payIns, paySuccess, returnMsg, returnData = Payment.objects.savePayment(
                    reqData,
                    PaymentSerializer
                )
                onSuccessMsg = "Payment Details Added Successfully"
            if payIns:
                return Response({"error": 0, "detail": onSuccessMsg, "data": payIns}, status=status.HTTP_201_CREATED)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITH_SAVE":
            reqData["docstatus"] = "U"
            reqData.pop("number")  # prevent to change voucher number
            pay_key = reqData.get('key')

            payIns, paySuccess, returnMsg, returnData = Payment.objects.submitPayment(
                reqData,
                PaymentSerializer,
                pay_key,
                {
                    "user":UF.getCurrentSessionUser(request),
                    "datetime":UF.getCurrentDateAndTime()
                },
            )
            if paySuccess:
                return Response({"error": 0, "detail": "Payment Details Saved Successfully", "data": payIns}, status=status.HTTP_201_CREATED)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # SUMIT WITH SAVE PROCESS
        if CURRENT_ACTION == "SUBMIT_WITHOUT_SAVE":
            reqData["docstatus"] = "U"
            reqData.pop("number")  # prevent to change voucher number
            pay_key = reqData.get('key')
            payIns, paySuccess, returnMsg, returnData = Payment.objects.submitPayment(
                reqData,
                PaymentSerializer,
                pay_key,
                {
                    "user":UF.getCurrentSessionUser(request),
                    "datetime":UF.getCurrentDateAndTime()
                },
                
            )
            if paySuccess:
                return Response({"error": 0, "detail": "Payment Details Saved Successfully", "data": payIns}, status=status.HTTP_201_CREATED)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)

        # CANCEL PROCESS
        if CURRENT_ACTION == "CANCEL":
            reqData["docstatus"] = "C"
            reqData.pop("number")  # prevent to change voucher number
            pay_key = reqData.get('key')
            payIns, paySuccess, returnMsg, returnData = Payment.objects.cancelPayment(
                pay_key,
                PaymentSerializer
            )
            if paySuccess:
                return Response({"error": 0, "detail": returnMsg, "data": payIns}, status=status.HTTP_201_CREATED)
            return Response({"error": 1, "detail": returnMsg, "data": returnData}, status=status.HTTP_400_BAD_REQUEST)


class PaymentAllocViewset(viewsets.GenericViewSet):
    queryset = Paymentalloc.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = PaymentAllocSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ).order_by('-key'))

        serializer = PaymentAllocSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        paymentAllocIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = PaymentAllocSerializer(paymentAllocIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        paymentAllocIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        paymentAllocIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        paymentAllocIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')
        serializer = PaymentAllocSerializer(
            paymentAllocIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Payment Allocation Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Payment Allocation PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Payment Allocation PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def rollback(self, pk):
        Paymentalloc.objects.filter(pay_key=pk).delete()

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        processedAllocations = []
        totalAllocatedAmount = float(0)
        payment_allocations = reqData.get('payment_allocations', [])
        for payAllocData in payment_allocations:

            payAllocData['pay_key'] = reqData.get('pay_key',)
            payAllocData['createdby'] = reqData.get('createdby')
            payAllocData['company'] = reqData.get('company')
            payAllocData['client_id'] = reqData.get('client_id')

            serializer = PaymentAllocSerializer(data=payAllocData)
            if serializer.is_valid():
                if serializer.save():
                    totalAllocatedAmount += float(payAllocData['allocamt'])
                    processedAllocations.append(serializer.data)
            else:
                self.rollback(reqData.get('pay_key'))
                return Response({"error": 1, "detail": "Error In Payment Allocation Post Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        if len(payment_allocations) > 0 and len(processedAllocations) == len(payment_allocations):
            # success
            # Update Payment Table
            paymentIns = Payment.objects.get(key=reqData.get('pay_key'))
            payData = PaymentSerializer(paymentIns).data
            paidamt = float(payData['paidamt'])

            paymentIns.lastmodifiedby = reqData.get('createdby')
            paymentIns.lastmodifieddttm = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            paymentIns.allocatedamt = totalAllocatedAmount

            if totalAllocatedAmount == paidamt:
                paymentIns.docstatus = "FA"
            elif totalAllocatedAmount < paidamt:
                paymentIns.docstatus = "PA"
            elif totalAllocatedAmount == float(0):
                paymentIns.docstatus = "U"

            paymentIns.save()

            # Update VendorInvoice Table
            for payAllocData in payment_allocations:
                venInvoiceKey = payAllocData.get('vendinv_key', False)
                if venInvoiceKey:
                    vendInvcIns = Vendorinvoice.objects.get(key=venInvoiceKey)
                    vendInvcData = VendorInvoiceSerializer(vendInvcIns).data
                    invcAmount = float(vendInvcData['invamt'])

                    vendInvcIns.lastmodifiedby = reqData.get('createdby')
                    vendInvcIns.lastmodifieddttm = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    vendInvcIns.balamt = totalAllocatedAmount

                    if totalAllocatedAmount == float(0):
                        vendInvcIns.docstatus = "FP"
                    elif totalAllocatedAmount > float(0):
                        vendInvcIns.docstatus = "PP"
                    elif totalAllocatedAmount == invcAmount:
                        vendInvcIns.docstatus = "U"

                    vendInvcIns.save()

            return Response(
                {
                    "error": 0,
                    "detail": "Payment Allocation Mapped Successfully",
                    "data": processedAllocations
                },
                status=status.HTTP_201_CREATED
            )

        else:
            # rollback
            self.rollback(request.get('pay_key'))
            return Response(
                {
                    "error": 1,
                    "detail": "Error In Payment Allocation Post Request",
                    "data": {}
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentModeViewset(viewsets.ViewSet):
    queryset = Modeofpay.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ModeofpaySerializer

    def list(self, request):
        serializer = ModeofpaySerializer(
            self.queryset.all().order_by('-descr'), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        modeIns = get_object_or_404(self.queryset, pk=pk)
        serializer_class = ModeofpaySerializer(modeIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        modeIns = get_object_or_404(self.queryset, pk=pk)
        modeIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        modeIns = get_object_or_404(self.queryset, pk=pk)
        serializer = ModeofpaySerializer(
            modeIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Payment Mode Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Payment Mode PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Payment Mode PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = ModeofpaySerializer(data=request.data)
        if serializer.is_valid():

            try:
                modeIns = serializer.save()
                if modeIns:
                    return Response({"error": 0, "detail": "Payment Mode Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Payment Mode"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
