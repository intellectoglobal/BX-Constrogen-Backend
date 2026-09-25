from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from buildiq.utils import UtilFunctions
from buildiq.pagenation_configs import Pagination10PerPage
from . models import ContractServiceTemplateHdr, ContractServiceTemplateDtl, PaymentScheduleTemplateHdr, PaymentScheduleTemplateDtl, ItemKitTemplateHdr, ItemKitTemplateDtl, CustomerPaymentScheduleTemplateHdr, CustomerPaymentScheduleTemplateDtl
from . serializers import (ContractServiceTemplateHdrListSerializer,
                           ContractServiceTemplateHdrGetSerializer,
                           ContractServiceTemplateHdrSerializer,
                           ContractServiceTemplateDtlSerializer,
                           PaymentScheduleTemplateHdrSerializer,
                           PaymentScheduleTemplateHdrListSerializer,
                           PaymentScheduleTemplateHdrGetSerializer,
                           PaymentScheduleTemplateDtlSerializer,
                           ItemKitTemplateHdrSerializer,
                           ItemKitTemplateHdrGetSerializer,
                           ItemKitTemplateHdrListSerializer,
                           ItemKitTemplateDtlSerializer,
                           CustomerPaymentScheduleTemplateHdrSerializer,
                           CustomerPaymentScheduleTemplateHdrListSerializer,
                           CustomerPaymentScheduleTemplateHdrGetSerializer,
                           CustomerPaymentScheduleTemplateDtlSerializer,
                           )


class ContractServiceTemplateViewSet(viewsets.ModelViewSet):
    queryset = ContractServiceTemplateHdr.objects.all()
    serializer_class = ContractServiceTemplateHdrSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID
        ).order_by('-key')

        if request.GET.get("contract_type", False):
            qrySet = qrySet.filter(contract_type_key=request.GET.get("contract_type", False))
            serializer = ContractServiceTemplateHdrGetSerializer(
                qrySet, many=True)
            return Response(serializer.data)
        
        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = ContractServiceTemplateHdrListSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = ContractServiceTemplateHdrListSerializer(
                page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ContractServiceTemplateHdrListSerializer(
            qrySet, many=True)
        return Response(serializer.data)

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
                {'error': 1, "detail": f"Template with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ContractServiceTemplateHdrGetSerializer(
            qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qryset = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        qryset.delete()
        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['client_id'] = clientID
        hdr_serializer = ContractServiceTemplateHdrSerializer(
            data=req_data)

        if not hdr_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Hdr data", "data": hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            template_hdr = hdr_serializer.save()

            service_template_details = req_data.get('service_template_detail', [])
            for detail in service_template_details:
                dtl_data = {
                    'contractservice_template_hdr_key': template_hdr.key,
                    'service_desc': detail['service_desc'],
                    'uom': detail['uom'],
                    'client_id': clientID
                }
                dtl_serializer = ContractServiceTemplateDtlSerializer(
                    data=dtl_data)

                if dtl_serializer.is_valid():
                    dtl_serializer.save()
                else:
                    transaction.set_rollback(True)
                    return Response({"error": 1, "detail": "Error in Dtl data", "data": dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Added Successfully", "data": hdr_serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        # Main template data
        main_data = request.data
        main_key = pk

        hdr_instance = ContractServiceTemplateHdr.objects.get(
            pk=main_key, client_id=clientID)
        hdr_serializer = ContractServiceTemplateHdrSerializer(
            instance=hdr_instance, data=main_data, partial=True)

        if not hdr_serializer.is_valid():
            return Response(hdr_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hdr_serializer.save()

        service_template_details = main_data.get('service_template_detail', [])
        existing_service_templates = set(ContractServiceTemplateDtl.objects.filter(
            contractservice_template_hdr_key=main_key, client_id=clientID).values_list('key', flat=True))

        processed_keys = set()
        errors = []
        successes = []

        for detail_data in service_template_details:
            detail_key = detail_data.get('key')
            if detail_key is not None:
                processed_keys.add(detail_key)
                try:
                    service_template = ContractServiceTemplateDtl.objects.get(
                        key=detail_key, client_id=clientID)
                    action = 'updated'
                except ContractServiceTemplateDtl.DoesNotExist:
                    service_template = None
                    action = 'created'
            else:
                service_template = None
                action = 'created'

            detail_data['client_id'] = clientID
            detail_data['contractservice_template_hdr_key'] = main_key

            if service_template:
                service_template_serializer = ContractServiceTemplateDtlSerializer(
                    instance=service_template, data=detail_data, partial=True)
            else:
                service_template_serializer = ContractServiceTemplateDtlSerializer(
                    data=detail_data)

            if service_template_serializer.is_valid():
                service_template_serializer.save()
                successes.append(
                    {"action": action, "data": service_template_serializer.data})
            else:
                errors.append({"error": 1, "detail": f"Error in ContractServiceTemplateDtl data for id {detail_key}",
                              "data": service_template_serializer.errors})
        to_delete_keys = existing_service_templates - processed_keys
        if to_delete_keys:
            ContractServiceTemplateDtl.objects.filter(
                key__in=to_delete_keys, client_id=clientID).delete()

        if errors:
            return Response({"error": 1, "detail": "Errors in processing ContractServiceTemplateDtl data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 0, "detail": "ContractServiceTemplateDtls processed successfully", "data": successes}, status=status.HTTP_200_OK)


class PaymentScheduleTemplateViewSet(viewsets.ModelViewSet):
    queryset = PaymentScheduleTemplateHdr.objects.all()
    serializer_class = PaymentScheduleTemplateHdrSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(clientid=clientID).order_by('-key')

        if request.GET.get("contract_type", False):
            qrySet = qrySet.filter(contract_type_key=request.GET.get("contract_type", False))
            serializer = PaymentScheduleTemplateHdrGetSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = PaymentScheduleTemplateHdrListSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = PaymentScheduleTemplateHdrListSerializer(
                page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PaymentScheduleTemplateHdrListSerializer(
            qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(clientid=clientID, key=pk)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 1, "detail": f"Template with id {pk} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentScheduleTemplateHdrGetSerializer(
            qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qryset = get_object_or_404(
            self.queryset.filter(clientid=clientID), pk=pk)
        qryset.delete()
        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['clientid'] = clientID
        hdr_serializer = PaymentScheduleTemplateHdrSerializer(data=req_data)

        if not hdr_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Hdr data", "data": hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            template_hdr = hdr_serializer.save()

            payment_schedule_template_details = req_data.get('payment_schedule_template_detail', [])
            for detail in payment_schedule_template_details:
                dtl_data = {
                    'payment_schedule_template_hdr_key': template_hdr.key,
                    'payment_stage_desc': detail['payment_stage_desc'],
                    'clientid': clientID
                }
                dtl_serializer = PaymentScheduleTemplateDtlSerializer(
                    data=dtl_data)

                if dtl_serializer.is_valid():
                    dtl_serializer.save()
                else:
                    transaction.set_rollback(True)
                    return Response({"error": 1, "detail": "Error in Dtl data", "data": dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Added Successfully", "data": hdr_serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        main_data = request.data
        main_key = pk

        hdr_instance = PaymentScheduleTemplateHdr.objects.get(
            pk=main_key, clientid=clientID)
        hdr_serializer = PaymentScheduleTemplateHdrSerializer(
            instance=hdr_instance, data=main_data, partial=True)

        if not hdr_serializer.is_valid():
            return Response(hdr_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hdr_serializer.save()

        details = main_data.get('payment_schedule_template_detail', [])
        existing_details = set(PaymentScheduleTemplateDtl.objects.filter(
            payment_schedule_template_hdr_key=main_key, clientid=clientID).values_list('key', flat=True))

        processed_keys = set()
        errors = []
        successes = []

        for detail_data in details:
            detail_key = detail_data.get('key')
            if detail_key is not None:
                processed_keys.add(detail_key)
                try:
                    detail_instance = PaymentScheduleTemplateDtl.objects.get(
                        key=detail_key, clientid=clientID)
                    action = 'updated'
                except PaymentScheduleTemplateDtl.DoesNotExist:
                    detail_instance = None
                    action = 'created'
            else:
                detail_instance = None
                action = 'created'

            detail_data['clientid'] = clientID
            detail_data['payment_schedule_template_hdr_key'] = main_key

            if detail_instance:
                detail_serializer = PaymentScheduleTemplateDtlSerializer(
                    instance=detail_instance, data=detail_data, partial=True)
            else:
                detail_serializer = PaymentScheduleTemplateDtlSerializer(
                    data=detail_data)

            if detail_serializer.is_valid():
                detail_serializer.save()
                successes.append(
                    {"action": action, "data": detail_serializer.data})
            else:
                errors.append(
                    {"error": 1, "detail": f"Error in PaymentScheduleTemplateDtl data for id {detail_key}", "data": detail_serializer.errors})

        to_delete_keys = existing_details - processed_keys
        if to_delete_keys:
            PaymentScheduleTemplateDtl.objects.filter(
                key__in=to_delete_keys, clientid=clientID).delete()

        if errors:
            return Response({"error": 1, "detail": "Errors in processing PaymentScheduleTemplateDtl data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 0, "detail": "PaymentScheduleTemplateDtls processed successfully", "data": successes}, status=status.HTTP_200_OK)


class ItemKitTemplateViewSet(viewsets.ModelViewSet):
    queryset = ItemKitTemplateHdr.objects.all()
    serializer_class = ItemKitTemplateHdrSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        item_type = request.GET.get("item_type")
        purpose_key = request.GET.get("purpose_key")

        qrySet = self.queryset.filter(client_id=clientID).order_by('-key')

        if item_type and purpose_key:
            qrySet = qrySet.filter(item_type_key=item_type, purpose_key=purpose_key)

        if request.GET.get("without_pagination") == "1":
            serializer = ItemKitTemplateHdrGetSerializer(qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = ItemKitTemplateHdrListSerializer(
                page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ItemKitTemplateHdrListSerializer(
            qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(client_id=clientID, key=pk)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 1, "detail": f"Item kit with id {pk} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemKitTemplateHdrGetSerializer(
            qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qryset = get_object_or_404(
            self.queryset.filter(client_id=clientID), pk=pk)
        qryset.delete()
        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['client_id'] = clientID
        hdr_serializer = ItemKitTemplateHdrSerializer(data=req_data)

        if not hdr_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Hdr data", "data": hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            template_hdr = hdr_serializer.save()

            item_kit_template_details = req_data.get('item_kit_template_detail', [])
            for detail in item_kit_template_details:
                dtl_data = {
                    'item_kit_template_hdr_key': template_hdr.key,
                    'item_key': detail.get('item_key'),
                    'brand': detail.get('brand', None),
                    'model_number': detail.get('model_number', None),
                    'qty': detail.get('qty', None),
                    'item_uom_key': detail.get('item_uom_key'),
                    'client_id': clientID
                }
                dtl_serializer = ItemKitTemplateDtlSerializer(
                    data=dtl_data)

                if dtl_serializer.is_valid():
                    dtl_serializer.save()
                else:
                    transaction.set_rollback(True)
                    return Response({"error": 1, "detail": "Error in Dtl data", "data": dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Added Successfully", "data": hdr_serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        main_data = request.data
        main_key = pk

        hdr_instance = ItemKitTemplateHdr.objects.get(
            pk=main_key, client_id=clientID)
        hdr_serializer = ItemKitTemplateHdrSerializer(
            instance=hdr_instance, data=main_data, partial=True)

        if not hdr_serializer.is_valid():
            return Response(hdr_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hdr_serializer.save()

        details = main_data.get('item_kit_template_detail', [])
        existing_details = set(ItemKitTemplateDtl.objects.filter(
            item_kit_template_hdr_key=main_key, client_id=clientID).values_list('key', flat=True))

        processed_keys = set()
        errors = []
        successes = []

        for detail_data in details:
            detail_key = detail_data.get('key')
            if detail_key is not None:
                processed_keys.add(detail_key)
                try:
                    detail_instance = ItemKitTemplateDtl.objects.get(
                        key=detail_key, client_id=clientID)
                    action = 'updated'
                except ItemKitTemplateDtl.DoesNotExist:
                    detail_instance = None
                    action = 'created'
            else:
                detail_instance = None
                action = 'created'

            detail_data['client_id'] = clientID
            detail_data['item_kit_template_hdr_key'] = main_key

            if detail_instance:
                detail_serializer = ItemKitTemplateDtlSerializer(
                    instance=detail_instance, data=detail_data, partial=True)
            else:
                detail_serializer = ItemKitTemplateDtlSerializer(
                    data=detail_data)

            if detail_serializer.is_valid():
                detail_serializer.save()
                successes.append(
                    {"action": action, "data": detail_serializer.data})
            else:
                errors.append(
                    {"error": 1, "detail": f"Error in ItemKitTemplateDtlSerializer data for id {detail_key}", "data": detail_serializer.errors})

        to_delete_keys = existing_details - processed_keys
        if to_delete_keys:
            ItemKitTemplateDtl.objects.filter(
                key__in=to_delete_keys, client_id=clientID).delete()

        if errors:
            return Response({"error": 1, "detail": "Errors in processing ItemKitTemplateDtlSerializer data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 0, "detail": "ItemKitTemplateDtlSerializer processed successfully", "data": successes}, status=status.HTTP_200_OK)


class CustomerPaymentScheduleTemplateViewSet(viewsets.ModelViewSet):
    queryset = CustomerPaymentScheduleTemplateHdr.objects.all()
    serializer_class = CustomerPaymentScheduleTemplateHdrSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(clientid=clientID).order_by('-key')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = CustomerPaymentScheduleTemplateHdrGetSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = CustomerPaymentScheduleTemplateHdrListSerializer(
                page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CustomerPaymentScheduleTemplateHdrListSerializer(
            qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(clientid=clientID, key=pk)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 1, "detail": f"Template with id {pk} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerPaymentScheduleTemplateHdrGetSerializer(
            qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qryset = get_object_or_404(
            self.queryset.filter(clientid=clientID), pk=pk)
        qryset.delete()
        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['clientid'] = clientID
        hdr_serializer = CustomerPaymentScheduleTemplateHdrSerializer(data=req_data)

        if not hdr_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Hdr data", "data": hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            template_hdr = hdr_serializer.save()

            payment_schedule_template_details = req_data.get('payment_schedule_template_detail', [])
            for detail in payment_schedule_template_details:
                dtl_data = {
                    'payment_schedule_template_hdr_key': template_hdr.key,
                    'payment_stage_desc': detail['payment_stage_desc'],
                    'clientid': clientID
                }
                dtl_serializer = CustomerPaymentScheduleTemplateDtlSerializer(
                    data=dtl_data)

                if dtl_serializer.is_valid():
                    dtl_serializer.save()
                else:
                    transaction.set_rollback(True)
                    return Response({"error": 1, "detail": "Error in Dtl data", "data": dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Added Successfully", "data": hdr_serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        main_data = request.data
        main_key = pk

        hdr_instance = CustomerPaymentScheduleTemplateHdr.objects.get(
            pk=main_key, clientid=clientID)
        hdr_serializer = CustomerPaymentScheduleTemplateHdrSerializer(
            instance=hdr_instance, data=main_data, partial=True)

        if not hdr_serializer.is_valid():
            return Response(hdr_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hdr_serializer.save()

        details = main_data.get('payment_schedule_template_detail', [])
        existing_details = set(CustomerPaymentScheduleTemplateDtl.objects.filter(
            payment_schedule_template_hdr_key=main_key, clientid=clientID).values_list('key', flat=True))

        processed_keys = set()
        errors = []
        successes = []

        for detail_data in details:
            detail_key = detail_data.get('key')
            if detail_key is not None:
                processed_keys.add(detail_key)
                try:
                    detail_instance = CustomerPaymentScheduleTemplateDtl.objects.get(
                        key=detail_key, clientid=clientID)
                    action = 'updated'
                except CustomerPaymentScheduleTemplateDtl.DoesNotExist:
                    detail_instance = None
                    action = 'created'
            else:
                detail_instance = None
                action = 'created'

            detail_data['clientid'] = clientID
            detail_data['payment_schedule_template_hdr_key'] = main_key

            if detail_instance:
                detail_serializer = CustomerPaymentScheduleTemplateDtlSerializer(
                    instance=detail_instance, data=detail_data, partial=True)
            else:
                detail_serializer = CustomerPaymentScheduleTemplateDtlSerializer(
                    data=detail_data)

            if detail_serializer.is_valid():
                detail_serializer.save()
                successes.append(
                    {"action": action, "data": detail_serializer.data})
            else:
                errors.append(
                    {"error": 1, "detail": f"Error in CustomerPaymentScheduleTemplateDtl data for id {detail_key}", "data": detail_serializer.errors})

        to_delete_keys = existing_details - processed_keys
        if to_delete_keys:
            CustomerPaymentScheduleTemplateDtl.objects.filter(
                key__in=to_delete_keys, clientid=clientID).delete()

        if errors:
            return Response({"error": 1, "detail": "Errors in processing CustomerPaymentScheduleTemplateDtl data", "data": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 0, "detail": "CustomerPaymentScheduleTemplateDtls processed successfully", "data": successes}, status=status.HTTP_200_OK)

