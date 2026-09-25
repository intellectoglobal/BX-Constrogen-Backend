from django.shortcuts import render
from django.db import transaction
from rest_framework import generics
from rest_framework.views import APIView
from .models import (Purpose, Warehouse, Item,
                     Itemtype, Itemuom, Uomtype, Itemgroup,
                     Itemgroupdetail, Itemsubtype, ItemSubtypeSpecification, ItemSubtypeItemUOM, ItemSpecification, ItemItemUOM, ItemPurpose, Brand)
from .serializers import (PurposeSerializer, WarehouseSerializer,
                          ItemSerializer, ItemuomSerializer, ItemtypeSerializer, UOMTypeSerializer, ItemGroupSerializer,
                          ItemGroupDetailSerializer, ItemSubtypeSerializer, ItemSpecificationSerializer, ItemItemUOMSerializer, ItemSubtypeSpecificationSerializer, ItemSubtypeItemUOMSerializer, ItemPurposeSerializer, BrandSerializer, ItemRateSerializer)
from vendor.models import VendorItemType
from vendor.serializers import VendorItemTypeSerializer
from pricing.models import PurchaseorderItems
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from datetime import datetime
from buildiq.utils import UtilFunctions
from rest_framework.permissions import AllowAny
from buildiq.pagenation_configs import Pagination10PerPage, Pagination5PerPage
from django.db.models import F, ExpressionWrapper, DecimalField, Max
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError

# Create your views here.


class PurposeViewset(viewsets.GenericViewSet):
    queryset = Purpose.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = PurposeSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if request.GET.get("item_type", False):
            qset = self.queryset.filter(
                client_id=clientID,
                itemtyp_key=request.GET.get("item_type")
            ).order_by('-key')
            serializer = PurposeSerializer(qset, many=True)
            return Response(serializer.data)

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = PurposeSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:

            if request.GET.get("type", False):
                qrySet = qrySet.filter(itemtyp_key=request.GET.get("type"))

            page = self.paginate_queryset(qrySet)
            serializer = PurposeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purposeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = PurposeSerializer(purposeIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purposeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = PurposeSerializer(
            purposeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Purpose Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Purpose PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Purpose PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        purposeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        purposeIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = PurposeSerializer(data=reqData)
        if serializer.is_valid():
            try:
                purposeIns = serializer.save()
                if purposeIns:
                    return Response({"error": 0, "detail": "Purpose Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Purpose"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class WarehouseViewset(viewsets.GenericViewSet):
    queryset = Warehouse.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = WarehouseSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            client_id=clientID).order_by('-key'))
        serializer = WarehouseSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        warehouseIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = WarehouseSerializer(warehouseIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        warehouseIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = WarehouseSerializer(
            warehouseIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Warehouse Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Warehouse PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Warehouse PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        warehouseIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        warehouseIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['id'] = Warehouse().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = WarehouseSerializer(data=reqData)
        if serializer.is_valid():
            try:
                warehouseIns = serializer.save()
                if warehouseIns:
                    return Response({"error": 0, "detail": "Warehouse Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Warehouse"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemTypeViewset(viewsets.GenericViewSet):
    queryset = Itemtype.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ItemtypeSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')

        vendor_key = request.GET.get("vendor_key", None)
        if vendor_key and UF.isNum(vendor_key):
            qrySet = qrySet.filter(
                key__in=VendorItemType.objects.filter(vend_key=vendor_key)
                .values_list("item_type_key", flat=True)
            )

        if request.GET.get("type", False) and UF.isNum(request.GET.get("type")):
                qrySet = qrySet.filter(key=request.GET.get("type"))

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ItemtypeSerializer(
                qrySet, many=True, fields=('key', 'descr'))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = ItemtypeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = ItemtypeSerializer(itemTypeIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ItemtypeSerializer(
            itemTypeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Item Type Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Item Type PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Item Type PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        itemTypeIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ItemtypeSerializer(data=reqData)
        if serializer.is_valid():
            try:
                itemTypeIns = serializer.save()
                if itemTypeIns:
                    return Response({"error": 0, "detail": "Item Type Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Item Type"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemSubTypeViewset(viewsets.GenericViewSet):
    queryset = Itemsubtype.objects.all()
    serializer_class = ItemSubtypeSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('item_type', False):
            qset = self.queryset.filter(
                client_id=clientID,
                itemtyp_key=request.GET.get('item_type')
            ).order_by('descr')

            serializer = ItemSubtypeSerializer(qset, many=True)
            return Response(serializer.data)
        else:
            qrySet = self.queryset.filter(
                client_id=clientID).order_by('-key')

            if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
                serializer = ItemSubtypeSerializer(
                    qrySet, many=True, fields=('key', 'id', 'descr'))
                return Response(serializer.data)
            else:
                if request.GET.get('type', False):
                    qrySet = qrySet.filter(itemtyp_key=request.GET.get('type'))

                page = self.paginate_queryset(qrySet)
                serializer = ItemSubtypeSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemSubTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = ItemSubtypeSerializer(itemSubTypeIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemSubTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        itemSubTypeIns.delete()
        return Response("Delete Success")

    @transaction.atomic
    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData = request.data
        reqData['client_id'] = clientID
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        serializer = ItemSubtypeSerializer(data=reqData)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    itemSubtypeIns = serializer.save()

                    if itemSubtypeIns:
                        itemSubtypeKey = itemSubtypeIns.key
                        currentUser = UF.getCurrentSessionUser(request)
                        currentDate = UF.getCurrentDateAndTime()

                        spec_errors = []
                        uom_errors = []

                        for spec in reqData.get("specifications", []):
                            spec["item_subtype_key"] = itemSubtypeKey
                            spec["createdby"] = currentUser
                            spec["createddttm"] = currentDate
                            spec["client_id"] = clientID

                            spec_serializer = ItemSubtypeSpecificationSerializer(
                                data=spec)
                            if spec_serializer.is_valid():
                                spec_serializer.save()
                            else:
                                spec_errors.append({
                                    "spec": spec,
                                    "errors": spec_serializer.errors
                                })

                        for uom in reqData.get("uoms", []):
                            uom["item_subtype_key"] = itemSubtypeKey
                            uom["createdby"] = currentUser
                            uom["createddttm"] = currentDate
                            uom["client_id"] = clientID

                            uom_serializer = ItemSubtypeItemUOMSerializer(
                                data=uom)
                            if uom_serializer.is_valid():
                                uom_serializer.save()
                            else:
                                uom_errors.append({
                                    "uom": uom,
                                    "errors": uom_serializer.errors
                                })

                        if spec_errors or uom_errors:
                            return Response({
                                "error": 1,
                                "detail": "There were errors with specifications or UOMs",
                                "spec_errors": spec_errors,
                                "uom_errors": uom_errors
                            }, status=status.HTTP_400_BAD_REQUEST)

                        return Response({"error": 0, "detail": "Item Subtype Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 1, "detail": "Invalid Data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            item_subtype = Itemsubtype.objects.get(key=pk, client_id=clientID)
        except Itemsubtype.DoesNotExist:
            return Response({"error": 1, "detail": "Item Subtype does not exist"}, status=status.HTTP_404_NOT_FOUND)

        reqData = request.data
        reqData['client_id'] = clientID
        currentUser = UF.getCurrentSessionUser(request)

        item_subtype_serializer = ItemSubtypeSerializer(
            item_subtype, data=reqData, partial=True)

        if item_subtype_serializer.is_valid():
            try:
                with transaction.atomic():
                    item_subtype_serializer.save()

                    processed_specification_keys = []
                    processed_uom_keys = []

                    for specification_data in reqData.get('specifications', []):
                        specification_key = specification_data.get('key')
                        if specification_key:
                            specification = ItemSubtypeSpecification.objects.get(
                                pk=specification_key, client_id=clientID)
                            specification_serializer = ItemSubtypeSpecificationSerializer(
                                instance=specification, data=specification_data, partial=True)
                        else:
                            specification_data['item_subtype_key'] = item_subtype.key
                            specification_data['createdby'] = currentUser
                            specification_data['client_id'] = clientID
                            specification_serializer = ItemSubtypeSpecificationSerializer(
                                data=specification_data)

                        if specification_serializer.is_valid():
                            specification_serializer.save()
                            processed_specification_keys.append(
                                specification_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": specification_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    for uom_data in reqData.get('uoms', []):
                        uom_key = uom_data.get('key')
                        if uom_key:
                            uom = ItemSubtypeItemUOM.objects.get(
                                pk=uom_key, client_id=clientID)
                            uom_serializer = ItemSubtypeItemUOMSerializer(
                                instance=uom, data=uom_data, partial=True)
                        else:
                            uom_data['item_subtype_key'] = item_subtype.key
                            uom_data['createdby'] = currentUser
                            uom_data['client_id'] = clientID
                            uom_serializer = ItemSubtypeItemUOMSerializer(
                                data=uom_data)

                        if uom_serializer.is_valid():
                            uom_serializer.save()
                            processed_uom_keys.append(
                                uom_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": uom_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    ItemSubtypeSpecification.objects.filter(item_subtype_key=item_subtype.key).exclude(
                        key__in=processed_specification_keys).delete()

                    ItemSubtypeItemUOM.objects.filter(item_subtype_key=item_subtype.key).exclude(
                        key__in=processed_uom_keys).delete()

                    return Response({"error": 0, "detail": "Item Subtype Updated Successfully", "data": item_subtype_serializer.data}, status=status.HTTP_200_OK)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": 1, "detail": "Error in Item Subtype data", "data": item_subtype_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemUomViewset(viewsets.GenericViewSet):
    queryset = Itemuom.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ItemuomSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get("item_type", False):
            qrySet = self.queryset.filter(
                client_id=clientID,
                itemtyp_key=request.GET.get('item_type')
            ).order_by('descr')
            serializer = ItemuomSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            qrySet = self.queryset.filter(
                client_id=clientID
            ).order_by('descr')

            if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
                serializer = ItemuomSerializer(
                    qrySet, many=True, fields=('key', 'descr'))
                return Response(serializer.data)
            else:
                if request.GET.get('type', False):
                    qrySet = qrySet.filter(itemtyp_key=request.GET.get('type'))
                page = self.paginate_queryset(qrySet)
                serializer = ItemuomSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemUOMIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = ItemuomSerializer(itemUOMIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemUOMIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ItemuomSerializer(
            itemUOMIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Item UOM Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Item UOM PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Item UOM PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemUOMIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        itemUOMIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ItemuomSerializer(data=reqData)
        if serializer.is_valid():
            try:
                itemUOMIns = serializer.save()
                if itemUOMIns:
                    return Response({"error": 0, "detail": "Item UOM Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Item UOM"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemViewset(viewsets.GenericViewSet):
    queryset = Item.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ItemSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()

        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if request.GET.get('item_type', False):
            qrySet = qrySet.filter(itemtyp_key=request.GET.get('item_type'))
        
        item_types = request.GET.get('item_types', None)
        if item_types:
            item_type_list = item_types.split(",")
            qrySet = qrySet.filter(itemtyp_key__in=item_type_list).order_by('descr')

        if request.GET.get('item_sub_type', False):
            qrySet = qrySet.filter(subtype=request.GET.get('item_sub_type'))

        if request.GET.get('vendor', False):
            vendorId = request.GET.get('vendor')
            if VendorItemType.objects.filter(vend_key=vendorId).exists():
                VendorItemTypeSerial = VendorItemTypeSerializer(
                    VendorItemType.objects.filter(vend_key=vendorId), many=True)
                itemTypes = [each['item_type_key']
                             for each in VendorItemTypeSerial.data]
                qrySet = qrySet.filter(itemtyp_key__in=itemTypes)

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ItemSerializer(
                qrySet, many=True, fields=('key', 'id', 'descr', 'gst', 'itemtyp_key', 'itemuom_key', 'itemuom_list', ))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = ItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = ItemSerializer(itemIns)
        return Response(serializer_class.data)

    @transaction.atomic
    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            itemIns = Item.objects.get(key=pk, client_id=clientID)
        except Item.DoesNotExist:
            return Response({"error": 1, "detail": "Item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        reqData = request.data
        currentUser = UF.getCurrentSessionUser(request)
        reqData['lastmodifiedby'] = currentUser
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        item_serializer = ItemSerializer(itemIns, data=reqData, partial=True)
        if item_serializer.is_valid():
            try:
                with transaction.atomic():
                    item_serializer.save()

                    processed_specification_keys = []
                    for spec_data in reqData.get('specifications', []):
                        spec_key = spec_data.get('key')
                        if spec_key:
                            specification = ItemSpecification.objects.get(
                                pk=spec_key, client_id=clientID)
                            specification_serializer = ItemSpecificationSerializer(
                                instance=specification, data=spec_data, partial=True)
                        else:
                            spec_data['item_key'] = pk
                            spec_data['createdby'] = currentUser
                            spec_data['client_id'] = clientID
                            specification_serializer = ItemSpecificationSerializer(
                                data=spec_data)

                        if specification_serializer.is_valid():
                            specification_serializer.save()
                            processed_specification_keys.append(
                                specification_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": "Error in specification data", "data": specification_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    # Process UOMs
                    processed_uom_keys = []
                    for uom_data in reqData.get('uoms', []):
                        uom_key = uom_data.get('key')
                        if uom_key:
                            uom = ItemItemUOM.objects.get(
                                pk=uom_key, client_id=clientID)
                            uom_serializer = ItemItemUOMSerializer(
                                instance=uom, data=uom_data, partial=True)
                        else:
                            uom_data['item_key'] = pk
                            uom_data['createdby'] = currentUser
                            uom_data['client_id'] = clientID
                            uom_serializer = ItemItemUOMSerializer(
                                data=uom_data)

                        if uom_serializer.is_valid():
                            uom_serializer.save()
                            processed_uom_keys.append(
                                uom_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": "Error in UOM data", "data": uom_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    # Process Purposes
                    processed_purpose_keys = []
                    for purpose_key in reqData.get('purpose', []):
                        purpose_instance = ItemPurpose.objects.filter(
                            item_key=pk, purpose_key=purpose_key, client_id=clientID).first()

                        if purpose_instance:
                            processed_purpose_keys.append(purpose_instance.key)
                        else:
                            purpose_data = {
                                'item_key': pk,
                                'client_id': clientID,
                                'purpose_key': purpose_key,
                            }
                            purpose_serializer = ItemPurposeSerializer(
                                data=purpose_data)

                            if purpose_serializer.is_valid():
                                purpose_serializer.save()
                                processed_purpose_keys.append(
                                    purpose_serializer.instance.key)
                            else:
                                return Response({"error": 1, "detail": "Error in purpose data", "data": purpose_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    # Clean up old data
                    ItemSpecification.objects.filter(item_key=pk).exclude(
                        key__in=processed_specification_keys).delete()
                    ItemItemUOM.objects.filter(item_key=pk).exclude(
                        key__in=processed_uom_keys).delete()
                    ItemPurpose.objects.filter(item_key=pk).exclude(
                        key__in=processed_purpose_keys).delete()

                    return Response({"error": 0, "detail": "Item Updated Successfully", "data": item_serializer.data}, status=status.HTTP_200_OK)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response({"error": 1, "detail": "Error in Item data", "data": item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        itemIns.delete()
        return Response("Delete Success")

    @transaction.atomic
    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData = request.data
        currentUser = UF.getCurrentSessionUser(request)

        reqData['client_id'] = clientID
        reqData['createdby'] = currentUser

        serializer = self.serializer_class(data=reqData)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    itemIns = serializer.save()
                    if itemIns:
                        itemKey = itemIns.key
                        spec_errors = []
                        uom_errors = []
                        purpose_errors = []

                        for spec in reqData['specifications']:
                            spec['item_key'] = itemKey
                            spec['item_subtype_spec_key'] = spec['key']
                            spec['created_by'] = currentUser
                            spec['client_id'] = clientID
                            spec.pop('lastmodifiedby')
                            spec.pop('lastmodifieddttm')

                            spec_serializer = ItemSpecificationSerializer(
                                data=spec)
                            if spec_serializer.is_valid():
                                spec_serializer.save()
                            else:
                                spec_errors.append({
                                    "spec": spec,
                                    "errors": spec_serializer.errors
                                })

                        for uom in reqData['uoms']:
                            uom_data = {
                                'item_key': itemKey,
                                'item_uom_key': uom,
                                'createdby': currentUser,
                                'client_id': clientID
                            }

                            uom_serializer = ItemItemUOMSerializer(
                                data=uom_data)
                            if uom_serializer.is_valid():
                                uom_serializer.save()
                            else:
                                uom_errors.append({
                                    "uom": uom,
                                    "errors": uom_serializer.errors
                                })

                        for purpose in reqData['purpose']:
                            purpose_data = {
                                'item_key': itemKey,
                                'purpose_key': purpose,
                                'client_id': clientID
                            }

                            purpose_serializer = ItemPurposeSerializer(
                                data=purpose_data)
                            if purpose_serializer.is_valid():
                                purpose_serializer.save()
                            else:
                                purpose_errors.append({
                                    "purpose": purpose,
                                    "errors": purpose_serializer.errors
                                })

                        if spec_errors or uom_errors or purpose_errors:
                            return Response({
                                "error": 1,
                                "detail": "There were errors with specifications or UOMs or Purpose",
                                "spec_errors": spec_errors,
                                "uom_errors": uom_errors,
                                "purpose_errors": purpose_errors
                            }, status=status.HTTP_400_BAD_REQUEST)

                        return Response({"error": 0, "detail": "Item Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 1, "detail": "Invalid Data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemRateViewSet(generics.ListAPIView):
    serializer_class = ItemRateSerializer
    pagination_class = Pagination5PerPage  # 5 per page, max 10 rows total = 2 pages

    def get_queryset(self):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(self.request)
        if not isValid:
            raise ValidationError(returnObj['message'])

        item_key = self.request.query_params.get('item_key')
        brand = self.request.query_params.get('brand')
        model = self.request.query_params.get('model')

        queryset = PurchaseorderItems.objects.filter(
            item_key=item_key,
            company_id=companyID,
            client_id=clientID,
            po_key__vendorinvoice__isnull=False,
            qty__gt=0
        )

        if brand:
            queryset = queryset.filter(brand=brand)
        if model:
            queryset = queryset.filter(model_number__iexact=model)

        queryset = (
            queryset
            .annotate(
                invoicedate=Max('po_key__vendorinvoice__invoicedate'),
                rate_without_gst=ExpressionWrapper(
                    F('netamt') / F('qty'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                ),
                rate_with_gst=ExpressionWrapper(
                    (F('netamt') + Coalesce(F('gstamt'), 0)) / F('qty'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .order_by('-invoicedate')
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        items = list(queryset)

        if not items:
            if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
                return Response({"results": [], "summary": None})

            page = self.paginate_queryset([])
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data["summary"] = None
            return Response(response_data)

        highest = max(items, key=lambda x: x.rate_without_gst)
        lowest = min(items, key=lambda x: x.rate_without_gst)
        summary = {
            "item_name": highest.item_key.descr if highest.item_key else None,
            "item_brand": highest.brand.name if highest.brand else None,
            "item_uom": highest.item_uom_key.descr if highest.item_uom_key else None,
            "highest": self.get_serializer(highest).data,
            "lowest": self.get_serializer(lowest).data,
        }

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.get_serializer(items, many=True)
            return Response({"results": serializer.data, "summary": summary})

        page = self.paginate_queryset(items)
        serializer = self.get_serializer(page, many=True)
        response_data = self.get_paginated_response(serializer.data).data
        response_data["summary"] = summary
        return Response(response_data)


class ItemModelViewSet(APIView):
    pagination_class = Pagination10PerPage

    def get(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = PurchaseorderItems.objects.filter(
            client_id=clientID,
            company_id=companyID,
        )
        item_key = request.query_params.get('item')
        if item_key:
            queryset = queryset.filter(item_key=item_key)

        brand_key = request.query_params.get('brand')
        if brand_key:
            queryset = queryset.filter(brand=brand_key)

        model_numbers = (
            queryset
            .exclude(model_number__isnull=True)
            .exclude(model_number='')
            .values_list('model_number', flat=True)
            .distinct()
            .order_by('model_number')
        )
        results = [{"name": value} for value in model_numbers]

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            return Response(results)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request)
        return paginator.get_paginated_response(page)


class UomTypeViewset(viewsets.GenericViewSet):
    queryset = Uomtype.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = UOMTypeSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('name')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = UOMTypeSerializer(qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        serializer = UOMTypeSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        uomTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = UOMTypeSerializer(uomTypeIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        uomTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = UOMTypeSerializer(
            uomTypeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "UOM Type updated successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In UOM Type PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In UOM Type PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        uomTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        uomTypeIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['id'] = Uomtype().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = UOMTypeSerializer(data=reqData)
        if serializer.is_valid():
            # try:
            if serializer.save():
                return Response({"error": 0, "detail": "UOM Type Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            # except:
            #     return Response({"error": 1, "detail": "Error While Adding UOM Type"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemGroupViewset(viewsets.GenericViewSet):
    queryset = Itemgroup.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ItemGroupSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            client_id=clientID).order_by('-key'))
        serializer = ItemGroupSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemGrpIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = ItemGroupSerializer(itemGrpIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemGrpIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ItemGroupSerializer(
            itemGrpIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Item Group updated successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Item Group PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Item Group PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemGrpIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        itemGrpIns.delete()
        return Response("Delete Success")

    def rollBack(self, itemGrpKey):
        Itemgroupdetail.objects.filter(itemgrp_key=itemGrpKey).delete()
        Itemgroup.objects.get(key=itemGrpKey).delete()

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['id'] = Itemgroup().nextID()

        if reqData.get("key", False) and Itemgroup.objects.filter(key=reqData.get("key")).exists():
            reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
            reqData['lastmodifieddttm'] = datetime.today().strftime(
                '%Y-%m-%d %H:%M:%S')
            itemGrpIns = get_object_or_404(
                self.queryset, pk=reqData.get("key"))
            itmGrpserializer = ItemGroupSerializer(
                itemGrpIns, data=reqData, partial=True)
            onSuccessMsg = "Item Group Modified Successfully."
        else:
            reqData['createdby'] = UF.getCurrentSessionUser(request)
            itmGrpserializer = ItemGroupSerializer(data=reqData)
            onSuccessMsg = "Item Group Added Successfully."

        addedItemGrpDetails = []
        if itmGrpserializer.is_valid():
            try:
                if itmGrpserializer.save():
                    itemGrpKey = itmGrpserializer.data['key']

                    # delete existing details records
                    Itemgroupdetail.objects.filter(
                        itemgrp_key=itemGrpKey).delete()

                    for itmGrpDtl in reqData['item_group_details']:
                        itmGrpDtl['itemgrp_key'] = itemGrpKey
                        itmGrpDtl['company_id'] = reqData['company']
                        itmGrpDtl['client_id'] = reqData['client_id']
                        itmGrpDtl['createdby'] = reqData['createdby']

                        itmGrpDetailserializer = ItemGroupDetailSerializer(
                            data=itmGrpDtl)

                        if itmGrpDetailserializer.is_valid():
                            itmGrpDetailserializer.save()
                            addedItemGrpDetails.append(
                                itmGrpDetailserializer.data)
                        else:
                            self.rollBack(itemGrpKey)
                            return Response({"error": 1, "detail": "Error While Adding Item Group Details", "data": itmGrpDetailserializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    if len(addedItemGrpDetails) == len(reqData['item_group_details']):
                        itmGrpOutput = itmGrpserializer.data
                        itmGrpOutput['item_group_details'] = addedItemGrpDetails
                        return Response({"error": 0, "detail": onSuccessMsg, "data": itmGrpOutput}, status=status.HTTP_201_CREATED)
                    else:
                        self.rollBack(itemGrpKey)
                        return Response({"error": 1, "detail": "Error While Adding Item Group Details"}, status=status.HTTP_400_BAD_REQUEST)

            except:
                return Response({"error": 1, "detail": "Error While Adding Item Group"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": itmGrpserializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemGroupDetailViewset(viewsets.GenericViewSet):
    queryset = Itemgroupdetail.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ItemGroupDetailSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.all()
        if request.GET.get('item_group_key', False):
            qrySet = self.queryset.filter(
                itemgrp_key=request.GET.get('item_group_key'),
                client_id=clientID
            )
        serializer = ItemGroupDetailSerializer(
            qrySet.filter(
                client_id=clientID
            ).order_by('-key'), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemGrpDtlIns = get_object_or_404(self.queryset.filter(client_id=clientID,
                                                               company_id=companyID), pk=pk)
        serializer_class = ItemGroupDetailSerializer(itemGrpDtlIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemGrpDtlIns = get_object_or_404(
            self.queryset.filter(client_id=clientID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ItemGroupDetailSerializer(
            itemGrpDtlIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Item Group Detail updated successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Item Group Detail PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Item Group Detail PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        itemGrpDtlIns = get_object_or_404(
            self.queryset.filter(client_id=clientID), pk=pk)
        itemGrpDtlIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ItemGroupDetailSerializer(data=reqData)
        if serializer.is_valid():
            try:
                if serializer.save():
                    return Response({"error": 0, "detail": "Item Group Detail Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Item Group Detail"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class BrandViewset(viewsets.GenericViewSet):
    queryset = Brand.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = BrandSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if request.GET.get("item_type", False):
            qset = self.queryset.filter(
                client_id=clientID,
                itemtyp_key=request.GET.get("item_type")
            ).order_by('name')
            serializer = BrandSerializer(qset, many=True)
            return Response(serializer.data)

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = BrandSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:

            if request.GET.get("type", False):
                qrySet = qrySet.filter(itemtyp_key=request.GET.get("type"))

            page = self.paginate_queryset(qrySet)
            serializer = BrandSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        brandIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = BrandSerializer(brandIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        brandIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = BrandSerializer(
            brandIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Brand Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error In Brand PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": f"Error In Brand PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        brandIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        brandIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = BrandSerializer(data=reqData)
        if serializer.is_valid():
            try:
                purposeIns = serializer.save()
                if purposeIns:
                    return Response({"error": 0, "detail": "Brand Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error While Adding Brand: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": f"Error in API request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

