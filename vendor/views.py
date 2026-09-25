from django.shortcuts import render
from .models import Vendortype, Vendorgroup, Vendor, Apterms, VendorItemType, VendorInvAllocAmt, VendorPaymentVoucherHdr, VendorPaymentVoucherDtl
from pricing.models import Vendorinvoice
from .serializers import VendorTypeSerializer, VendorGroupSerializer, ApTermsSerializer, VendorSerializer, VendorItemTypeSerializer, PayVendorInvoiceSerializer, PayVendorSerializer, VendorInvAllocAmtSerializer, VendorVoucherHdrSerializer, VendorVoucherHdrListSerializer, VendorVoucherHdrGetSerializer, VendorVoucherDtlSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from buildiq.utils import UtilFunctions
from datetime import datetime
from buildiq.pagenation_configs import Pagination10PerPage
from django.db.models import Q
from django.db import transaction
from collections import defaultdict
from decimal import Decimal
from tax.models import TdsEntry, TdsReport, PurchaseGstEntry, PurchaseGstReport
from tax.serializers import TdsEntrySerializer, TdsReportSerializer, PurchaseGstEntrySerializer, PurchaseGstReportSerializer
from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce

# Create your views here.


class VendorTypeViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Vendortype.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = VendorTypeSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID, company=companyID).order_by('-key')

        if(request.GET.get("contractors", False)):
            if request.GET.get("contractors") == "1":
                qrySet = qrySet.filter(contractor="Y")
            else:
                qrySet = qrySet.filter(contractor="N")

        if(request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = VendorTypeSerializer(
                qrySet, many=True, fields=('key', 'descr'))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = VendorTypeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)
        serializer_class = VendorTypeSerializer(vendorTypeIns)
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

        serializer = VendorTypeSerializer(
            vendorTypeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Vendor Type Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendoe Type PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor Type PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = VendorTypeSerializer(data=reqData)

        if reqData['contractor'].upper() == "Y":
            successMsg = "Contractor Type Added Successfully"
        else:
            successMsg = "Vendor Type Added Successfully"

        if serializer.is_valid():
            try:
                costCatIns = serializer.save()
                if costCatIns:
                    return Response({"error": 0, "detail": successMsg, "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Vendor Type"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorGroupViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Vendorgroup.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = VendorGroupSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            client_id=clientID, company=companyID).order_by('-key'))
        serializer = VendorGroupSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorGroupIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)
        serializer_class = VendorGroupSerializer(vendorGroupIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorGroupIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = VendorGroupSerializer(
            vendorGroupIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Vendor Group Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Vendor Group PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor Group PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorGroupIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company=companyID), pk=pk)

        vendorGroupIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['id'] = Vendorgroup().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = VendorGroupSerializer(data=reqData)
        if serializer.is_valid():
            try:
                costCatIns = serializer.save()
                if costCatIns:
                    return Response({"error": 0, "detail": "Vendor Group Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Vendor Group"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ApTermsViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Apterms.objects.all()
    serializer_class = ApTermsSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID,
            company=companyID
        ).order_by('-key')
        reqField = ('key', 'id', 'descr', 'days')

        if(request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ApTermsSerializer(
                qrySet, many=True, read_only=True, fields=reqField)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = ApTermsSerializer(
                page, many=True, read_only=True, fields=reqField)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vApTermsIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company=companyID
        ), pk=pk)
        serializer_class = ApTermsSerializer(vApTermsIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vApTermsIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company=companyID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ApTermsSerializer(
            vApTermsIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "AP Term Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In AP Term PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In AP Term PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vApTermsIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company=companyID
        ), pk=pk)
        vApTermsIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['id'] = Apterms().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ApTermsSerializer(data=reqData)
        if serializer.is_valid():
            try:
                costCatIns = serializer.save()
                if costCatIns:
                    return Response({"error": 0, "detail": "AP Term Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding AP Term"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Vendor.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = VendorSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        
        querySet = self.queryset.filter(
            client_id=clientID,
            company=companyID
        ).order_by('name')
        
        if request.GET.get("type", False) and UF.isNum(request.GET.get("type")):
                querySet = querySet.filter(vendtyp_key=request.GET.get("type"))     
        
        if request.GET.get("vendor", False) and UF.isNum(request.GET.get("vendor")):
                querySet = querySet.filter(key=request.GET.get("vendor"))     

        if (request.GET.get("filter", False) and int(request.GET.get("filter")) == 1):
            serializer = VendorSerializer(querySet, many=True, fields=['key', 'name']) 
            return Response(serializer.data)  

        page = self.paginate_queryset(querySet)          
            
        serializer = VendorSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company=companyID
        ), pk=pk)

        if request.GET.get('item_type_alone', False):
            serializer_class = VendorSerializer(
                vendorIns, fields=('itemtype',))
            return Response(serializer_class.data['itemtype'])
        else:
            serializer_class = VendorSerializer(vendorIns)
            return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company=companyID
        ), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = VendorSerializer(
            vendorIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                successMessage = "Vendor Updated Successfully"
                    
                
                processedKeys = []
                success=0
                for itemtype in reqData.get("itemtypes",[]):
                    if itemtype.get('key', False) and VendorItemType.objects.filter(pk=itemtype.get('key')).exists():
                        # old item
                        print("Vendor Item Type key found :: Update Required")
                        VendorItemTypeIns = VendorItemType.objects.get(pk=itemtype.get('key'))
                        vendorItemTypeSer = VendorItemTypeSerializer(VendorItemTypeIns, data=itemtype, partial=True)
                    else:
                        # new item
                        print("Vendor Item Type key Not found :: Insert Required")
                        itemtype['vend_key'] = pk
                        itemtype['company'] = companyID
                        itemtype['client_id'] = clientID
                        vendorItemTypeSer = VendorItemTypeSerializer(data=itemtype)
                    
                    if vendorItemTypeSer.is_valid():
                        try:
                            vendorItemTypeSer.save()
                            print("Vendor Item Type Insert or Update Success !!!", vendorItemTypeSer.data['key'])
                            processedKeys.append(vendorItemTypeSer.data['key'])
                            success += 1
                        except Exception as e:
                            print(e)
                            return Response({"error": 1, "detail": "Error While Updating Vendor Item Type"}, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({"error": 1,"detail": "Error in API request", "data": vendorItemTypeSer.errors}, status=status.HTTP_400_BAD_REQUEST)
                

                if success == len(reqData.get('itemtypes',[])):
                    # delete removed items
                    print("Processed Vendor Item Type Keys :: ",processedKeys, " Delete Remaining" )
                    VendorItemType.objects.filter(vend_key=pk).exclude(key__in=processedKeys).delete()
                    return Response({"error": 0, "detail": successMessage, "data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": 1, "detail": "Error In Vendor Item Type update"}, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                print(e)
                return Response({"error": 1, "detail": "Error In Vendor PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Vendor PUT Request. Check The Data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        vendorIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company=companyID
        ), pk=pk)
        vendorIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        
        reqData = request.data
        reqData['company'] = companyID
        reqData['client_id'] = clientID
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        
        vendorSerializer = VendorSerializer(data=reqData)
        if vendorSerializer.is_valid():
            try:
                vendorIns = vendorSerializer.save()
                if vendorIns:
                    successMessage = "Vendor Added Successfully"
                    processedKeys = []
                    for itemtype in reqData.get("itemtypes",[]):
                        itemtype['vend_key'] = vendorIns.key
                        itemtype['company'] = companyID
                        itemtype['client_id'] = clientID
                        
                        serializer = VendorItemTypeSerializer(data=itemtype)
                        if serializer.is_valid():
                            try:
                                VendorItemTypeInstance = serializer.save()
                                processedKeys.append(serializer.data['key'])
                            except Exception as e:
                                print(e)
                                VendorItemType.objects.filter(key__in=processedKeys).delete()
                                vendorIns.delete()  
                                return Response({"error": 1, "detail": "Error While Adding Vendor Item Types"}, status=status.HTTP_400_BAD_REQUEST)                              
                        else:
                            print("Error occured deleting item types :: ", processedKeys)
                            VendorItemType.objects.filter(key__in=processedKeys).delete()
                            vendorIns.delete()  
                            return Response({"error": 1, "detail": "Error While Adding Vendor Item Types","data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)                              
                            
                    return Response({"error": 0, "detail": successMessage, "data": vendorSerializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(e)
                return Response({"error": 1, "detail": "Error While Adding Vendor"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": vendorSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorAllViewset(viewsets.ViewSet):
    queryset = Vendor.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = VendorSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])


        serialisedData = VendorSerializer(
            self.queryset.filter(
                inactive='N',
                client_id=clientID,
                company=companyID
            ).order_by('name'),
            many=True,
            fields=(
                'key',
                'name',
                'type',
            )
        ).data
        return Response(serialisedData)



class VendorPaymentAllViewSet(viewsets.ModelViewSet):
    pagination_class = Pagination10PerPage

    def list(self, request):              
        pay_invoice = request.query_params.get('pay_invoice')
        pay_vendor = request.query_params.get('pay_vendor')

        if pay_invoice:
            return self.get_pay_invoice_details(request)
        
        elif pay_vendor:
            return self.get_pay_vendor_details(request)

        return Response({'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def get_pay_invoice_details(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        
        querySet = Vendorinvoice.objects.filter(
            company=companyID,
            client_id=clientID
        ).exclude(invoice_status='P')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = PayVendorInvoiceSerializer(querySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(querySet)
        if page is not None:
            serializer = PayVendorInvoiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)


        serializer = PayVendorInvoiceSerializer(querySet, many=True)
        return Response(serializer.data)

    def format_aggregated_results(self, data):
        results = []
        for item in data:
            results.append({
                "key": item["vend_key__key"],
                "pending_amount": float(item["pending_amount"]),
                "allocated_amount": float(item["allocated_amount"]) if item["allocated_amount"] is not None else None,
                "vendor_details": {
                    "key": item["vend_key__key"],
                    "name": item["vend_key__name"]
                },
                "netamt": float(item["netamt"])
            })
        return results

    def get_pay_vendor_details(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        aggregated_qs = Vendorinvoice.objects.filter(
            company=companyID,
            client_id=clientID
        ).exclude(invoice_status='P').values(
            'vend_key__key',
            'vend_key__name'
        ).annotate(
            pending_amount=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F('netamt') - Coalesce(F('paid_amount'), Value(0), output_field=DecimalField()),
                        output_field=DecimalField()
                    )
                ),
                Value(0),
                output_field=DecimalField()
            ),
            allocated_amount=Coalesce(Sum('vendorinvallocamt__allocated_amount'), None, output_field=DecimalField()),
            netamt=Coalesce(Sum('netamt'), Value(0), output_field=DecimalField())
        ).order_by('vend_key__name')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            return Response(self.format_aggregated_results(aggregated_qs))

        page = self.paginate_queryset(aggregated_qs)
        if page is not None:
            return self.get_paginated_response(self.format_aggregated_results(page))

        return Response(self.format_aggregated_results(aggregated_qs))


class VendorInvAllocAmtView(viewsets.ModelViewSet):
        queryset = VendorInvAllocAmt.objects.all()
        serializer_class = VendorInvAllocAmtSerializer
        pagination_class = Pagination10PerPage

        def list(self,request):
            invoice_id = request.query_params.get('invoice_id')
            vendor_id = request.query_params.get('vendor_id')
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])
            if invoice_id:
                UF = UtilFunctions()
                isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
                if not isValid:
                    return Response(returnObj['message'], status=returnObj['http_status'])
                
                querySet = Vendorinvoice.objects.filter(
                    company=companyID,
                    client_id=clientID,
                    invoiceno = invoice_id
                ).exclude(invoice_status='P')
                print("querySet",querySet)
                if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
                    serializer = PayVendorInvoiceSerializer(querySet, many=True)
                    return Response(serializer.data)

                page = self.paginate_queryset(querySet)
                if page is not None:
                    serializer = PayVendorInvoiceSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)


                serializer = PayVendorInvoiceSerializer(querySet, many=True)
                return Response(serializer.data)
        
            elif vendor_id:
                querySet = Vendorinvoice.objects.filter(
                        company=companyID,
                        client_id=clientID,
                        vend_key=vendor_id
                    ).exclude(invoice_status='P')

                if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
                    serializer = PayVendorSerializer(querySet, many=True)
                    return Response(serializer.data)

                page = self.paginate_queryset(querySet)
                if page is not None:
                    serializer = PayVendorSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = PayVendorSerializer(querySet, many=True)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 1, "detail": "invalid request parameters"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        def update(self, request, pk=None):
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])

            invoices = request.data.get('invoices', [])

            errors = []
            successes = []

            for invoice_data in invoices:
                allocated_amount_details = invoice_data.get('allocated_amount_details')

                if allocated_amount_details is None:
                    invoice_id = invoice_data.get('key')
                    existing_alloc_objs = VendorInvAllocAmt.objects.filter(invoice_id=invoice_id, client_id=clientID)
                    if existing_alloc_objs.exists():
                        existing_alloc_objs.delete()
                    continue

                allocated_amount_key = allocated_amount_details.get('key')

                if allocated_amount_key is not None:
                    try:
                        vendor_inv_alloc_amt = VendorInvAllocAmt.objects.get(key=allocated_amount_key, client_id=clientID)
                        action = 'updated'
                    except VendorInvAllocAmt.DoesNotExist:
                        vendor_inv_alloc_amt = None
                        action = 'created'
                else:
                    vendor_inv_alloc_amt = None
                    action = 'created'

                invoice_data['client_id'] = clientID
                invoice_data['invoice_id'] = invoice_data['key']
                invoice_data['allocated_amount'] = allocated_amount_details['allocated_amount']

                if vendor_inv_alloc_amt:
                    vendor_inv_alloc_amt_serializer = VendorInvAllocAmtSerializer(
                        instance=vendor_inv_alloc_amt, data=invoice_data, partial=True)
                else:
                    if invoice_data.get('allocated_amount') is not None:
                        vendor_inv_alloc_amt_serializer = VendorInvAllocAmtSerializer(data=invoice_data)
                    else:
                        continue

                if vendor_inv_alloc_amt_serializer.is_valid():
                    vendor_inv_alloc_amt_serializer.save()
                    successes.append({"action": action, "data": vendor_inv_alloc_amt_serializer.data})
                else:
                    errors.append({"error": 1, "detail": f"Error in VendorInvAllocAmt data for id {allocated_amount_key}", "data": vendor_inv_alloc_amt_serializer.errors})

            if errors:
                return Response({"error": 1, "detail": "Errors in processing VendorInvAllocAmt data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": 0, "detail": "VendorInvAllocAmts processed successfully", "data": successes}, status=status.HTTP_200_OK)

        def delete(self, request,pk=None):
            UF = UtilFunctions()
            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])

            VendorInvAllocAmt_obj = get_object_or_404(self.queryset.filter(
                client_id=clientID,
                key=pk,
            )).delete()

            return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)        
    

class VendorVoucherViewSet(viewsets.ModelViewSet):
    queryset = VendorPaymentVoucherHdr.objects.all()
    serializer_class = VendorVoucherHdrSerializer
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
            serializer = VendorVoucherHdrListSerializer(qrySet, many=True)
            return Response(serializer.data)

        if request.GET.get("year") and request.GET.get("month"):
            year = request.GET.get("year")
            month = request.GET.get("month")
            qrySet = self.queryset.filter(
                company_id=companyID,
                client_id=clientID,
                vendor_voucher_dt__year = year,
                vendor_voucher_dt__month = month
            ).order_by('-key')

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = VendorVoucherHdrListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = VendorVoucherHdrListSerializer(qrySet, many=True)
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

        serializer = VendorVoucherHdrGetSerializer(qrySet, many=False)
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
                
                vendor_voucher_hdr_key = qrySet.key
                vendor_voucher_dtl = VendorPaymentVoucherDtl.objects.filter(vendor_voucher_hdr=vendor_voucher_hdr_key)
                
                for voucher in vendor_voucher_dtl:
                    voucher_paid_amount = voucher.paid_amount
                    vendor_invoice_obj = Vendorinvoice.objects.get(key=voucher.invoice_id.key)
                    
                    invoice_paid_amount = vendor_invoice_obj.paid_amount
                    balance_amount = invoice_paid_amount - voucher_paid_amount
                    
                    vendor_invoice_obj.paid_amount = balance_amount
                    
                    if balance_amount == 0.00:
                        vendor_invoice_obj.invoice_status = 'O'
                    else:
                        vendor_invoice_obj.invoice_status = 'A'
                    
                    vendor_invoice_obj.save()

                    if vendor_invoice_obj.tdsamt:
                        if vendor_invoice_obj.invoice_status == 'O':
                            
                            tds_entry_instance = TdsEntry.objects.filter(
                                vendor_invoice=vendor_invoice_obj.key
                            ).first()

                            if tds_entry_instance:
                                month = tds_entry_instance.date.month
                                year = tds_entry_instance.date.year
                                vendor = vendor_invoice_obj.vend_key

                                tds_report_instance = TdsReport.objects.filter(
                                    vendor=vendor,
                                    date__month=month,
                                    date__year=year
                                ).first()

                                if tds_report_instance:
                                    tds_report_instance.amount -= vendor_invoice_obj.tdsamt
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

                    if vendor_invoice_obj.gstamt:
                        if vendor_invoice_obj.invoice_status == 'O':
                            
                            gst_entry_instance = PurchaseGstEntry.objects.filter(
                                invoice=vendor_invoice_obj.key
                            ).first()

                            if gst_entry_instance:
                                month = gst_entry_instance.date.month
                                year = gst_entry_instance.date.year
                                vendor = vendor_invoice_obj.vend_key

                                gst_report_instance = PurchaseGstReport.objects.filter(
                                    vendor=vendor,
                                    date__month=month,
                                    date__year=year
                                ).first()

                                if gst_report_instance:
                                    gst_report_instance.gst_amount -= vendor_invoice_obj.gstamt
                                    if gst_report_instance.gst_amount <= 0.00:
                                        gst_report_instance.delete()
                                    else:
                                        gst_report_instance.save()
                                else:
                                    return Response(
                                        {"error": "Purchase GST Report instance not found for the given month and year"},
                                        status=status.HTTP_404_NOT_FOUND
                                    )
                                gst_entry_instance.delete()
            
                qrySet.delete()

                return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"Vendor Voucher with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return Response({"detail": "Delete Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID
        voucher_no = UF.getValidDocId(req_data['voucher_number'], "VVN", clientID)
        req_data['voucher_number'] = voucher_no
        vendor_voucher_hdr_serializer = VendorVoucherHdrSerializer(data=req_data)

        if not vendor_voucher_hdr_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Vendor Voucher Hdr data", "data": vendor_voucher_hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            vendor_voucher_hdr = vendor_voucher_hdr_serializer.save()

            invoices = req_data.get('invoices', [])
            for invoice_data in invoices:
                allocated_amount = invoice_data.get('allocated_amount')
                if allocated_amount is None:
                    return Response({"error": 1, "detail": "Allocated amount missing for an invoice"}, status=status.HTTP_400_BAD_REQUEST)

                invoice_id = invoice_data.get('key')
                if invoice_id is None:
                    return Response({"error": 1, "detail": "Invoice key missing for creating VendorVoucherDtl"}, status=status.HTTP_400_BAD_REQUEST)

                dtl_data = {
                    'vendor_voucher_hdr': vendor_voucher_hdr.key,
                    'invoice_id': invoice_id,
                    'paid_amount': allocated_amount,
                    'client_id': clientID
                }
                vendor_voucher_dtl_serializer = VendorVoucherDtlSerializer(data=dtl_data)

                if vendor_voucher_dtl_serializer.is_valid():
                    vendor_voucher_dtl_serializer.save()
                else:
                    transaction.set_rollback(True)
                    return Response({"error": 1, "detail": "Error in Vendor Voucher Dtl data", "data": vendor_voucher_dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                allocated_amount_details = invoice_data.get('allocated_amount_details')
                if allocated_amount_details and 'key' in allocated_amount_details:
                    try:
                        alloc_amt_obj = VendorInvAllocAmt.objects.get(key=allocated_amount_details['key'])
                        alloc_amt_obj.delete()
                    except VendorInvAllocAmt.DoesNotExist:
                        transaction.set_rollback(True)
                        return Response({'error': 1, "detail": f"Vendor Invoice allocated amount with id {allocated_amount_details['key']} does not exist"}, status=status.HTTP_404_NOT_FOUND)

                try:
                    invoice_obj = Vendorinvoice.objects.get(key=invoice_id)
                    current_paid_amount = float(invoice_obj.paid_amount) if invoice_obj.paid_amount else 0.0
                    invoice_obj.paid_amount = current_paid_amount + float(allocated_amount)

                    if float(invoice_obj.paid_amount) == float(invoice_obj.netamt):
                        invoice_obj.invoice_status = 'P'
                    elif float(invoice_obj.paid_amount) < float(invoice_obj.netamt):
                        invoice_obj.invoice_status = 'A'

                    invoice_obj.save()
                    
                    if invoice_obj.gstamt is not None and invoice_obj.gstamt > 0.00:
                        purchase_gst_entry = PurchaseGstEntry.objects.filter(invoice = invoice_obj.key)
                        
                        if not purchase_gst_entry:
                            purchase_gst_entry_data = {
                                'date': datetime.today().date(),
                                'vendor': invoice_obj.vend_key.key,
                                'invoice': invoice_obj.key,
                                'gst_amount': invoice_obj.gstamt,
                                'client': clientID,
                                'company': companyID
                            }
                            purchase_gst_entry_serializer = PurchaseGstEntrySerializer(data=purchase_gst_entry_data)
                            if purchase_gst_entry_serializer.is_valid():
                                purchase_gst_entry_serializer.save()
                                purchase_gst_report_instance = PurchaseGstReport.objects.filter(
                                    vendor=invoice_obj.vend_key, date__month=datetime.today().month, date__year=datetime.today().year
                                ).first()

                                if purchase_gst_report_instance:
                                    purchase_gst_report_instance.gst_amount += invoice_obj.gstamt
                                    purchase_gst_report_instance.save()
                                else:
                                    purchase_gst_report_data = {
                                        'date': datetime.today().date(),
                                        'vendor': invoice_obj.vend_key.key,
                                        'gst_no': invoice_obj.vend_key.gstnumber,
                                        'gst_amount': invoice_obj.gstamt,
                                        'client': clientID,
                                        'company': companyID
                                    }
                                    purchase_gst_report_serializer = PurchaseGstReportSerializer(data=purchase_gst_report_data)
                                    if purchase_gst_report_serializer.is_valid():
                                        purchase_gst_report_serializer.save()
                                    else:
                                        transaction.set_rollback(True)
                                        return Response({'error':1, 'detail': "Error while processing the Purchase Gst Report for the vendor", 'data': purchase_gst_report_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                transaction.set_rollback(True)
                                return Response({'error': 1, 'detail': 'Error while saving the Purchase Gst Entry for the vendor invoice payment', 'data': purchase_gst_entry_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


                    if invoice_obj.tdsamt is not None and invoice_obj.tdsamt > 0.00:
                        tds_entry = TdsEntry.objects.filter(vendor_invoice = invoice_obj.key)
                        
                        if not tds_entry:
                            tds_entry_data = {
                                'date': datetime.today().date(),
                                'vendor_invoice': invoice_obj.key,
                                'invoice_type': 'V',
                                'amount': invoice_obj.tdsamt,
                                'payment_status': 'Unpaid',
                                'client': clientID,
                                'company': companyID
                            }
                            tds_entry_serializer = TdsEntrySerializer(data=tds_entry_data)
                            if tds_entry_serializer.is_valid():
                                tds_entry_serializer.save()
                                tds_report_instance = TdsReport.objects.filter(
                                    vendor=req_data['vendor_id'], date__month=datetime.today().month, date__year=datetime.today().year
                                ).first()

                                if tds_report_instance:
                                    tds_report_instance.amount += invoice_obj.tdsamt
                                    tds_report_instance.save()
                                else:
                                    tds_report_data = {
                                        'date': datetime.today().date(),
                                        'vendor': req_data['vendor_id'],
                                        'entity_type': 'V',
                                        'amount': invoice_obj.tdsamt,
                                        'payment_status': 'Unpaid',
                                        'client': clientID,
                                        'company': companyID
                                    }
                                    tds_report_serializer = TdsReportSerializer(data=tds_report_data)
                                    if tds_report_serializer.is_valid():
                                        tds_report_serializer.save()
                                    else:
                                        transaction.set_rollback(True)
                                        return Response({'error':1, 'detail': "Error while processing the TDS report for the vendor", 'data': tds_report_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                transaction.set_rollback(True)
                                return Response({'error': 1, 'detail': 'Error while saving the TDS Entry for the vendor invoice payment', 'data': tds_entry_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                except Vendorinvoice.DoesNotExist:
                    transaction.set_rollback(True)
                    return Response({'error': 1, "detail": f"Vendorinvoice with id {invoice_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"error": 0, "detail": "Vendor Voucher Added Successfully", "data": vendor_voucher_hdr_serializer.data}, status=status.HTTP_201_CREATED)
