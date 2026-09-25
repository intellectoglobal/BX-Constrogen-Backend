from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import ConstructionAgreement, ConstructionAgreementService, ConstructionAgreementPaymentSchedule
from .serializers import ConstructionAgreementSerializer, ConstructionAgreementListSerializer, ConstructionAgreementGetSerializer, ConstructionAgreementServiceSerializer, ConstructionAgreementPaymentScheduleSerializer
from buildiq.pagenation_configs import Pagination10PerPage
from buildiq.utils import UtilFunctions

class ConstructionAgreementViewSet(viewsets.ModelViewSet):
    queryset = ConstructionAgreement.objects.all()
    serializer_class = ConstructionAgreementSerializer
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
            serializer = ConstructionAgreementListSerializer(qrySet, many=True)
            return Response(serializer.data)

        if request.GET.get("project", False) and UF.isNum(request.GET.get("project")):
            qrySet = qrySet.filter(project_id=request.GET.get("project"))

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = ConstructionAgreementListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ConstructionAgreementListSerializer(qrySet, many=True)
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
                {'error': 1, "detail": f"construction agreement with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConstructionAgreementGetSerializer(qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        construction_agreement_obj = get_object_or_404(self.queryset.filter(
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
            req_data['id'] = ConstructionAgreement.nextID()
            req_data['company_id'] = companyID
            req_data['client_id'] = clientID
            updated_agreement_no = UF.getValidDocId(
                req_data['agreement_no'], "CA", clientID)
            req_data['agreement_no'] = updated_agreement_no

            construction_agrmnt_serializer = ConstructionAgreementSerializer(
                data=req_data)

            if construction_agrmnt_serializer.is_valid():
                construction_agreement = construction_agrmnt_serializer.save()
                construction_agrmnt_key = construction_agreement.key
                print("construction_agrmnt_id", construction_agrmnt_key)

                service_desc_errors = []
                payment_schedule_errors = []
                
                if 'service_descriptions' in req_data and req_data['service_descriptions']:
                    for service_desc_data in req_data['service_descriptions']:
                        service_desc_data['id'] = ConstructionAgreementService.nextID(
                        )
                        service_desc_data['construction_agreement_id'] = construction_agrmnt_key
                        service_desc_serializer = ConstructionAgreementServiceSerializer(
                            data=service_desc_data)

                        if service_desc_serializer.is_valid():
                            service_desc_serializer.save()
                        else:
                            service_desc_errors.append(
                                service_desc_serializer.errors)


                if 'payment_schedules' in req_data and req_data['payment_schedules']:
                    for payment_schedule_data in req_data['payment_schedules']:
                        payment_schedule_data['id'] = ConstructionAgreementPaymentSchedule.nextID(
                        )
                        payment_schedule_data['construction_agreement_id'] = construction_agrmnt_key
                        payment_schedule_serializer = ConstructionAgreementPaymentScheduleSerializer(
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
                        "service_desc_errors": service_desc_errors,
                        "payment_schedule_errors": payment_schedule_errors
                    }
                    return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"error": 1, "detail": "Error in Construction Agreement data", "data": construction_agrmnt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Construction Agreement Added Successfully", "data": construction_agrmnt_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            print("Exception occurred:", str(e))
            return Response({"error": 1, "detail": "An error occurred while creating the Construction Agreement.", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            construction_agreement = ConstructionAgreement.objects.get(key=pk)
        except ConstructionAgreement.DoesNotExist:
            return Response({"error": 1, "detail": "Construction Agreement does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID

        construction_agrmnt_serializer = ConstructionAgreementSerializer(
            construction_agreement, data=req_data, partial=True)

        if construction_agrmnt_serializer.is_valid():
            try:
                with transaction.atomic():
                    construction_agrmnt_serializer.save()

                    processed_service_desc_keys = []
                    processed_payment_schedule_keys = []

                    for service_desc_data in req_data.get('service_descriptions', []):
                        service_desc_key = service_desc_data.get('key')
                        if service_desc_key:
                            service_description = ConstructionAgreementService.objects.get(
                                pk=service_desc_key)
                            service_desc_serializer = ConstructionAgreementServiceSerializer(
                                instance=service_description, data=service_desc_data, partial=True)
                        else:
                            service_desc_data['construction_agreement_id'] = construction_agreement.key
                            service_desc_data['id'] = ConstructionAgreementService.nextID(
                            )
                            service_desc_serializer = ConstructionAgreementServiceSerializer(
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
                            payment_schedule = ConstructionAgreementPaymentSchedule.objects.get(
                                pk=payment_schedule_key)
                            payment_schedule_serializer = ConstructionAgreementPaymentScheduleSerializer(
                                instance=payment_schedule, data=payment_schedule_data, partial=True)
                        else:
                            payment_schedule_data['construction_agreement_id'] = construction_agreement.key
                            payment_schedule_data['id'] = ConstructionAgreementPaymentSchedule.nextID(
                            )
                            payment_schedule_serializer = ConstructionAgreementPaymentScheduleSerializer(
                                data=payment_schedule_data)

                        if payment_schedule_serializer.is_valid():
                            payment_schedule_serializer.save()
                            processed_payment_schedule_keys.append(
                                payment_schedule_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": payment_schedule_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    ConstructionAgreementService.objects.filter(construction_agreement_id=construction_agreement.key).exclude(
                        key__in=processed_service_desc_keys).delete()

                    ConstructionAgreementPaymentSchedule.objects.filter(construction_agreement_id=construction_agreement.key).exclude(
                        key__in=processed_payment_schedule_keys).delete()

                    return Response({"error": 0, "detail": "Construction Agreement Updated Successfully", "data": construction_agrmnt_serializer.data}, status=status.HTTP_200_OK)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": 1, "detail": "Error in Construction Agreement data", "data": construction_agrmnt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
