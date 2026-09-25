from django.shortcuts import render
from .models import (Customer, CustomerPurchaseReceipt, SaleAgreement,
                     SaleAgreementRateCard, SaleAgreementPaymentSchedule, SaleInvoice, SourceOfFund, SaleReceipt)
from .serializers import (CustomerSerializer, CustomerPurchaseReceiptSerializer, SaleAgreementSerializer, SaleAgreementListSerializer,
                          SaleAgreementGetSerializer, SaleAgreementRateCardSerializer, SaleAgreementPaymentScheduleSerializer, SaleInvoiceSerializer, ReceiveSaleInvoiceSerializer, SourceOfFundSerializer, SaleReceiptSerializer)
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from datetime import datetime
from buildiq.utils import UtilFunctions
from buildiq.pagenation_configs import Pagination10PerPage
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.db import transaction
from rest_framework.views import APIView
from tax.models import SalesGstEntry, SalesGstReport, SalesTds
from tax.serializers import SalesGstEntrySerializer, SalesGstReportSerializer, SalesTdsSerializer


class CustomerViewset(viewsets.GenericViewSet):
    queryset = Customer.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = CustomerSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ).order_by('name')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = CustomerSerializer(
                qrySet, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = CustomerSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        customerIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)
        serializer_class = CustomerSerializer(customerIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        customerIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)
        customerIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        customerIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company_id=companyID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = CustomerSerializer(
            customerIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Customer Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Customer PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Customer PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['company_id'] = companyID
        reqData['client_id'] = clientID
        # print(reqData['aadhaar_no'])
        reqData['id'] = Customer().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = CustomerSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Customer Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Customer"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CustomerPurchaseReceiptViewset(viewsets.GenericViewSet):
    queryset = CustomerPurchaseReceipt.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = CustomerPurchaseReceiptSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ).order_by('-key')

        project = request.GET.get("project")
        if project:
            qrySet = qrySet.filter(
                project_key=project, client_id=clientID, company_id=companyID).order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = CustomerPurchaseReceiptSerializer(
                qrySet, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = CustomerPurchaseReceiptSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        customerIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)
        serializer_class = CustomerPurchaseReceiptSerializer(customerIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        customerIns = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID
        ), pk=pk)
        customerIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        customerIns = get_object_or_404(self.queryset.filter(
            client_id=clientID, company_id=companyID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = CustomerPurchaseReceiptSerializer(
            customerIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Customer Purchase Invoice Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Customer Purchase Invoice PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Customer Purchase Invoice PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['company_id'] = companyID
        reqData['client_id'] = clientID
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = CustomerPurchaseReceiptSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Customer Purchase Invoice Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Customer Purchase Invoice"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ActiveCustomerViewset(viewsets.GenericViewSet):
    queryset = Customer.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = CustomerSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        activeCustomers = self.queryset.filter(
            Q(inactive="N") | Q(inactive__isnull=True),
            company=companyID,
            client_id=clientID
        )
        data = self.serializer_class(activeCustomers, many=True).data
        return Response(data)


class SaleAgreementViewSet(viewsets.ModelViewSet):
    queryset = SaleAgreement.objects.all()
    serializer_class = SaleAgreementSerializer
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
            serializer = SaleAgreementListSerializer(qrySet, many=True)
            return Response(serializer.data)

        if request.GET.get("project", False) and UF.isNum(request.GET.get("project")):
            qrySet = qrySet.filter(project_id=request.GET.get("project"))

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = SaleAgreementListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SaleAgreementListSerializer(qrySet, many=True)
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
                {'error': 1, "detail": f"Sale agreement with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SaleAgreementGetSerializer(qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        sale_agreement_obj = get_object_or_404(self.queryset.filter(
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
            req_data['id'] = SaleAgreement.nextID()
            req_data['company_id'] = companyID
            req_data['client_id'] = clientID
            updated_agreement_no = UF.getValidDocId(
                req_data['agreement_no'], "SLA", clientID)
            req_data['agreement_no'] = updated_agreement_no

            sale_agrmnt_serializer = SaleAgreementSerializer(
                data=req_data)

            if sale_agrmnt_serializer.is_valid():
                sale_agreement = sale_agrmnt_serializer.save()
                sale_agrmnt_key = sale_agreement.key
                print("sale_agrmnt_id", sale_agrmnt_key)

                rate_card_errors = []
                payment_schedule_errors = []

                if 'rate_cards' in req_data and req_data['rate_cards']:
                    for rate_card_data in req_data['rate_cards']:
                        rate_card_data['id'] = SaleAgreementRateCard.nextID(
                        )
                        rate_card_data['sale_agreement_id'] = sale_agrmnt_key
                        rate_card_serializer = SaleAgreementRateCardSerializer(
                            data=rate_card_data)

                        if rate_card_serializer.is_valid():
                            rate_card_serializer.save()
                        else:
                            rate_card_errors.append(
                                rate_card_serializer.errors)

                if 'payment_schedules' in req_data and req_data['payment_schedules']:
                    for payment_schedule_data in req_data['payment_schedules']:
                        payment_schedule_data['id'] = SaleAgreementPaymentSchedule.nextID(
                        )
                        payment_schedule_data['sale_agreement_id'] = sale_agrmnt_key
                        payment_schedule_serializer = SaleAgreementPaymentScheduleSerializer(
                            data=payment_schedule_data)

                        if payment_schedule_serializer.is_valid():
                            payment_schedule_serializer.save()
                        else:
                            payment_schedule_errors.append(
                                payment_schedule_serializer.errors)

                if rate_card_errors or payment_schedule_errors:
                    transaction.set_rollback(True)
                    error_detail = {
                        "error": 1,
                        "detail": "Error in Rate Card or Payment Schedule data",
                        "rate_card_errors": rate_card_errors,
                        "payment_schedule_errors": payment_schedule_errors
                    }
                    return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"error": 1, "detail": "Error in Sale Agreement data", "data": sale_agrmnt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Sale Agreement Added Successfully", "data": sale_agrmnt_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            print("Exception occurred:", str(e))
            return Response({"error": 1, "detail": "An error occurred while creating the Sale Agreement.", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            sale_agreement = SaleAgreement.objects.get(key=pk)
        except SaleAgreement.DoesNotExist:
            return Response({"error": 1, "detail": "Sale Agreement does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID

        sale_agrmnt_serializer = SaleAgreementSerializer(
            sale_agreement, data=req_data, partial=True)

        if sale_agrmnt_serializer.is_valid():
            try:
                with transaction.atomic():
                    sale_agrmnt_serializer.save()

                    processed_rate_card_keys = []
                    processed_payment_schedule_keys = []

                    for rate_card_data in req_data.get('rate_cards', []):
                        rate_card_key = rate_card_data.get('key')
                        if rate_card_key:
                            rate_card = SaleAgreementRateCard.objects.get(
                                pk=rate_card_key)
                            rate_card_serializer = SaleAgreementRateCardSerializer(
                                instance=rate_card, data=rate_card_data, partial=True)
                        else:
                            rate_card_data['sale_agreement_id'] = sale_agreement.key
                            rate_card_data['id'] = SaleAgreementRateCard.nextID(
                            )
                            rate_card_serializer = SaleAgreementRateCardSerializer(
                                data=rate_card_data)

                        if rate_card_serializer.is_valid():
                            rate_card_serializer.save()
                            processed_rate_card_keys.append(
                                rate_card_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": rate_card_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    for payment_schedule_data in req_data.get('payment_schedules', []):
                        payment_schedule_key = payment_schedule_data.get('key')
                        if payment_schedule_key:
                            payment_schedule = SaleAgreementPaymentSchedule.objects.get(
                                pk=payment_schedule_key)
                            payment_schedule_serializer = SaleAgreementPaymentScheduleSerializer(
                                instance=payment_schedule, data=payment_schedule_data, partial=True)
                        else:
                            payment_schedule_data['sale_agreement_id'] = sale_agreement.key
                            payment_schedule_data['id'] = SaleAgreementPaymentSchedule.nextID(
                            )
                            payment_schedule_serializer = SaleAgreementPaymentScheduleSerializer(
                                data=payment_schedule_data)

                        if payment_schedule_serializer.is_valid():
                            payment_schedule_serializer.save()
                            processed_payment_schedule_keys.append(
                                payment_schedule_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": payment_schedule_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    SaleAgreementRateCard.objects.filter(sale_agreement_id=sale_agreement.key).exclude(
                        key__in=processed_rate_card_keys).delete()

                    SaleAgreementPaymentSchedule.objects.filter(sale_agreement_id=sale_agreement.key).exclude(
                        key__in=processed_payment_schedule_keys).delete()

                    return Response({"error": 0, "detail": "Sale Agreement Updated Successfully", "data": sale_agrmnt_serializer.data}, status=status.HTTP_200_OK)

            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": 1, "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"error": 1, "detail": "Error in Sale Agreement data", "data": sale_agrmnt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SaleInvoiceViewSet(viewsets.ModelViewSet):
    queryset = SaleInvoice.objects.all()
    serializer_class = SaleInvoiceSerializer
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
            serializer = SaleInvoiceSerializer(qrySet, many=True)
            return Response(serializer.data)

        if request.GET.get("project", False) and UF.isNum(request.GET.get("project")):
            qrySet = qrySet.filter(project_id=request.GET.get("project"))

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = SaleInvoiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SaleInvoiceSerializer(qrySet, many=True)
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
                {'error': 1, "detail": f"Sale invoice with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SaleInvoiceSerializer(qrySet, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        try:
            sale_invoice_obj = SaleInvoice.objects.filter(
                company_id=companyID,
                client_id=clientID,
                key=pk,
            ).first()
            sale_invoice_obj.payment_schedule_id.stage_status = 'O'
            sale_invoice_obj.payment_schedule_id.save()
            sale_invoice_obj.delete()
        
        except SaleInvoice.DoesNotExist:
            return Response({"detail":"Sale Invoice does not exist"},status=status.HTTP_404_NOT_FOUND)
        
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
                req_data['invoice_id'], "SIN", clientID)
            req_data['invoice_id'] = updated_invoice_id
            stage_ins = SaleAgreementPaymentSchedule.objects.filter(key=req_data['payment_schedule_id']).first()
            stage_ins.stage_status='I'
            sale_invoice_serializer = SaleInvoiceSerializer(
                data=req_data)

            if sale_invoice_serializer.is_valid():
                stage_ins.save()
                sale_invoice_serializer.save()

            else:
                return Response({"error": 1, "detail": "Error in Sale Invoice data", "data": sale_invoice_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Sale Invoice Added Successfully", "data": sale_invoice_serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            print("Exception occurred:", str(e))
            return Response({"error": 1, "detail": "An error occurred while creating the Sale Invoice.", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            sale_invoice = SaleInvoice.objects.get(key=pk)
        except SaleInvoice.DoesNotExist:
            return Response({"error": 1, "detail": "Sale Invoice does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['company_id'] = companyID
        req_data['client_id'] = clientID
        schedule_from_payload = req_data['payment_schedule_id']
        schedule_from_db = sale_invoice.payment_schedule_id
        if schedule_from_payload != schedule_from_db:
            schedule_from_db.stage_status = "O"
            try:
                stage_ins = SaleAgreementPaymentSchedule.objects.filter(key=schedule_from_payload).first()
                stage_ins.stage_status="I"
            except SaleAgreementPaymentSchedule.DoesNotExist:
                return Response({"error": 1, "detail": "Sale Payment Schedule does not exists"}, status=status.HTTP_404_NOT_FOUND)
        sale_invoice_serializer = SaleInvoiceSerializer(
            instance=sale_invoice, data=req_data, partial=True)

        if sale_invoice_serializer.is_valid():
            schedule_from_db.save()
            stage_ins.save()
            sale_invoice_serializer.save()
            return Response({"error": 0, "detail": "Sale Invoice Updated Successfully", "data": sale_invoice_serializer.data}, status=status.HTTP_200_OK)

        else:
            return Response({"error": 1, "detail": "Error in Sale Invoice data", "data": sale_invoice_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SaleInvoiceAllView(APIView):

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id')
        unit_id = request.query_params.get('unit_id')
        agreement_id = request.query_params.get('agreement_id')
        all_schedules = request.query_params.get('all_schedules')

        if project_id and unit_id and not agreement_id:
            return self.get_agreement_details(project_id, unit_id)

        elif agreement_id and project_id and not unit_id:
            return self.get_invoice_details(project_id, agreement_id)
        
        elif agreement_id and all_schedules and not project_id and not unit_id:
            return self.get_agreement_payment_schedule_details(agreement_id, all_schedules=True)

        elif agreement_id and not project_id and not unit_id:
            return self.get_agreement_payment_schedule_details(agreement_id)

        return Response({'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def get_agreement_details(self, project_id, unit_id):

        agreements = SaleAgreement.objects.filter(
            project_id=project_id,
            unit_id=unit_id
        )

        agreements_data = []
        for agreement in agreements:
            agreement_data = {
                'key': agreement.key,
                'agreement_no': agreement.agreement_no,
                'paid_amount': agreement.paid_amount,
                'sale_amount': agreement.sale_amount
            }
            agreements_data.append(agreement_data)

        return Response(agreements_data)

    def get_agreement_payment_schedule_details(self, agreement_id, all_schedules=False):
        if all_schedules:
            payment_schedules = SaleAgreementPaymentSchedule.objects.filter(
                sale_agreement_id=agreement_id
            )
        else:
            payment_schedules = SaleAgreementPaymentSchedule.objects.filter(
                sale_agreement_id=agreement_id, stage_status="O"
            )
            
        serializer = SaleAgreementPaymentScheduleSerializer(
            payment_schedules, many=True)
        return Response(serializer.data)

    def get_invoice_details(self, project_id, agreement_id):
        invoices = SaleInvoice.objects.filter(
            agreement_id=agreement_id,
            project_id=project_id
        ).exclude(invoice_status="P")
        serializer = SaleInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class SalePaymentAllViewSet(viewsets.ModelViewSet):
    pagination_class = Pagination10PerPage

    def list(self, request):
        pay_invoice = request.query_params.get('receivable_invoices')

        if pay_invoice:
            return self.get_receivable_invoices_details(request)

        return Response({'error': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)

    def get_receivable_invoices_details(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project_id = request.query_params.get('project_id')
        unit_id = request.query_params.get('unit_id')

        if project_id and unit_id:
            querySet = SaleInvoice.objects.filter(
                project_id=project_id,
                agreement_id__unit_id=unit_id,
                company_id=companyID,
                client_id=clientID
            ).exclude(invoice_status='P').order_by('key')
        else:
            querySet = SaleInvoice.objects.none()

        page = self.paginate_queryset(querySet)
        if page is not None:
            serializer = ReceiveSaleInvoiceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReceiveSaleInvoiceSerializer(querySet, many=True)
        return Response(serializer.data)

class SourceOfFundViewSet(viewsets.GenericViewSet):
    queryset = SourceOfFund.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = SourceOfFundSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.order_by('-key')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = SourceOfFundSerializer(qrySet, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = SourceOfFundSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        source_of_fund = get_object_or_404(self.queryset, pk=pk)
        serializer = SourceOfFundSerializer(source_of_fund)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        source_of_fund = get_object_or_404(self.queryset, pk=pk)
        source_of_fund.delete()
        return Response({"detail": "Source of Fund deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        source_of_fund = get_object_or_404(self.queryset, pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = SourceOfFundSerializer(
            source_of_fund, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Source of Fund updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({"error": 1, "detail": "Error in updating Source of Fund"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Invalid data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = SourceOfFundSerializer(data=reqData)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Source of Fund added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error in adding Source of Fund"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Invalid data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SaleReceiptViewSet(viewsets.ModelViewSet):
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project_id = request.GET.get("project_id")
        unit_id = request.GET.get("unit_id")
        year = request.GET.get("year")
        month = request.GET.get("month")
        agreement_id = request.GET.get("agreement_id")

        qrySet = self.queryset.filter(client_id=clientID, company_id=companyID)

        if project_id:
            qrySet = qrySet.filter(
                project_id=project_id,
            )
        
        if agreement_id:
            qrySet = qrySet.filter(
                invoice_id__agreement_id=agreement_id,
            )
            
        if unit_id:
            qrySet = qrySet.filter(
                unit_id=unit_id
            )

        if year and month:
            qrySet = qrySet.filter(
                date__year=year,
                date__month=month
            )

        qrySet = qrySet.order_by('-key')

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = SaleReceiptSerializer(qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = SaleReceiptSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SaleReceiptSerializer(qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        sale_receipt = get_object_or_404(self.queryset.filter(
            client_id=clientID, company_id=companyID), pk=pk)
        serializer = SaleReceiptSerializer(sale_receipt)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            with transaction.atomic():
                receipt_obj = self.queryset.get(
                    company=companyID,
                    client=clientID,
                    key=pk
                )

                try:
                    invoice_obj = SaleInvoice.objects.get(
                    key=receipt_obj.invoice_id.key)
                except SaleInvoice.DoesNotExist:
                    return Response(
                        {"error": f"Sale Invoice with key {receipt_obj.invoice_id.key} does not exist"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                invoice_paid_amount = invoice_obj.paid_amount
                balance_amount = invoice_paid_amount - receipt_obj.amount

                invoice_obj.paid_amount = balance_amount

                if balance_amount == 0.00:
                    invoice_obj.invoice_status = 'O'
                else:
                    invoice_obj.invoice_status = 'A'

                invoice_obj.save()
                if invoice_obj.agreement_id:
                    try:
                        agreement_obj = SaleAgreement.objects.get(
                            key=invoice_obj.agreement_id.key
                        )
                        current_agrmnt_paid_amount = agreement_obj.paid_amount if agreement_obj.paid_amount is not None else 0.00
                        updated_agrmnt_amt = current_agrmnt_paid_amount - receipt_obj.amount
                        agreement_obj.paid_amount = updated_agrmnt_amt
                        agreement_obj.save()

                    except SaleAgreement.DoesNotExist:
                        return Response(
                            {"error": f"Sale Agreement with id {invoice_obj.agreement_id.key} does not exist"},
                            status=status.HTTP_404_NOT_FOUND
                        )

                if invoice_obj.gst_amount:
                    if invoice_obj.invoice_status == 'O':

                        sale_gst_entry_instance = SalesGstEntry.objects.filter(
                            invoice=invoice_obj.key
                        ).first()

                        if sale_gst_entry_instance:
                            month = sale_gst_entry_instance.date.month
                            year = sale_gst_entry_instance.date.year
                            customer = sale_gst_entry_instance.customer

                            sale_gst_report_instance = SalesGstReport.objects.filter(
                               customer=customer,
                                date__month=month,
                                date__year=year
                            ).first()

                            if sale_gst_report_instance:
                                sale_gst_report_instance.gst_amount -= invoice_obj.gst_amount
                                if sale_gst_report_instance.gst_amount <= 0.00:
                                    sale_gst_report_instance.delete()
                                else:
                                    sale_gst_report_instance.save()
                            else:
                                return Response(
                                    {"error": "Sale GST Report instance not found for the given month and year"},
                                    status=status.HTTP_404_NOT_FOUND
                                )
                            sale_gst_entry_instance.delete()
                
                if invoice_obj.is_tds_invoice:
                    if invoice_obj.invoice_status == 'O':

                        sale_tds_instance = SalesTds.objects.filter(
                            invoice=invoice_obj.key
                        ).first()

                        if sale_tds_instance:
                            sale_tds_instance.delete()
                receipt_obj.delete()

                return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)

        except receipt_obj.DoesNotExist:
            return Response(
                {'error': f"Sale Receipt with id {pk} does not exist"},
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
        req_data['company'] = companyID
        req_data['client'] = clientID
        receipt_number = UF.getValidDocId(req_data['receipt_number'], "SR", clientID)
        req_data['receipt_number'] = receipt_number
        invoice_id = req_data['invoice_id']
        try:
            invoice_obj = SaleInvoice.objects.get(key=invoice_id)
        except SaleInvoice.DoesNotExist:
            return Response({'error': 1, "detail": f"Sale Invoice with id {invoice_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        req_data['customer_id'] = invoice_obj.agreement_id.customer_id.key
        req_data['unit_id'] = invoice_obj.agreement_id.unit_id.key
        amount = req_data['amount']
        print("amount from payload", amount)
        sale_receipt_serializer = SaleReceiptSerializer(
            data=req_data)

        if not sale_receipt_serializer.is_valid():
            return Response({"error": 1, "detail": "Error in Sale Receipt data", "data": sale_receipt_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            current_paid_amount = float(
                invoice_obj.paid_amount) if invoice_obj.paid_amount else 0.0
            print("current_paid_amount", current_paid_amount)

            invoice_obj.paid_amount = current_paid_amount + \
                float(amount)
            print("updated paid_amount", invoice_obj.paid_amount)
            
            if float(invoice_obj.paid_amount) == float(invoice_obj.invoice_amount):
                invoice_obj.invoice_status = 'P'
            elif float(invoice_obj.paid_amount) < float(invoice_obj.invoice_amount):
                invoice_obj.invoice_status = 'A'

            if invoice_obj.agreement_id:
                agreement_obj = SaleAgreement.objects.get(
                    key=invoice_obj.agreement_id.key)
                if agreement_obj.paid_amount is None:
                    agreement_obj.paid_amount = 0

                agreement_obj.paid_amount += amount
                print("updated agreement paid amount", agreement_obj.paid_amount)

                agreement_obj.save()

            invoice_obj.save()

            if invoice_obj.is_tds_invoice:
                sales_tds_report_ins = SalesTds.objects.filter(invoice=invoice_obj.key)
                if not sales_tds_report_ins:
                    sales_tds_report_data = {
                        'date': datetime.today().date(),
                        'project': invoice_obj.project_id.key,
                        'unit': invoice_obj.agreement_id.unit_id.key,
                        'customer': invoice_obj.agreement_id.customer_id.key,
                        'invoice': invoice_obj.key,
                        'amount':invoice_obj.invoice_amount,
                        'payment_status':'Unpaid',
                        'client': clientID,
                        'company': companyID
                    }
                    sales_tds_report_serializer = SalesTdsSerializer(data=sales_tds_report_data)
                    if sales_tds_report_serializer.is_valid():
                        sales_tds_report_serializer.save()
                    else:
                        return Response({'error':1,'detail':'Error occured while processing Sales TDS Report','data':sales_tds_report_serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                    
            if invoice_obj.gst_amount:
                sales_gst_entry = SalesGstEntry.objects.filter(
                    invoice=invoice_obj.key)
                if not sales_gst_entry:
                    sales_gst_entry_data = {
                        'date': datetime.today().date(),
                        'project': invoice_obj.project_id.key,
                        'unit': invoice_obj.agreement_id.unit_id.key,
                        'customer': invoice_obj.agreement_id.customer_id.key,
                        'invoice': invoice_obj.key,
                        'gst_amount': invoice_obj.gst_amount,
                        'client': clientID,
                        'company': companyID
                    }
                    sales_gst_entry_serializer = SalesGstEntrySerializer(
                        data=sales_gst_entry_data)
                    if sales_gst_entry_serializer.is_valid():
                        sales_gst_entry_serializer.save()
                        sales_gst_report_instance = SalesGstReport.objects.filter(
                            customer=invoice_obj.agreement_id.customer_id, date__month=datetime.today(
                            ).month,
                            date__year=datetime.today().year
                        ).first()

                        if sales_gst_report_instance:
                            sales_gst_report_instance.gst_amount += invoice_obj.gst_amount
                            sales_gst_report_instance.save()
                        else:
                            sales_gst_report_data = {
                                'date': datetime.today().date(),
                                'customer': invoice_obj.agreement_id.customer_id.key,
                                'project': invoice_obj.project_id.key,
                                'unit': invoice_obj.agreement_id.unit_id.key,
                                'agreement': invoice_obj.agreement_id.key,
                                'gst_amount': invoice_obj.gst_amount,
                                'client': clientID,
                                'company': companyID
                            }
                            sales_gst_report_serializer = SalesGstReportSerializer(
                                data=sales_gst_report_data)
                            if sales_gst_report_serializer.is_valid():
                                sales_gst_report_serializer.save()
                            else:
                                transaction.set_rollback(True)
                                return Response({'error': 1, 'detail': "Error occured while processing the Sale GST report", 'data': sales_gst_report_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        transaction.set_rollback(True)
                        return Response({'error': 1, 'detail': 'Error occured while saving the Sale GST Entry for the invoice payment', 'data': sales_gst_entry_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        sale_receipt_serializer.save()            
        return Response({"error": 0, "detail": "Sale Receipt Added Successfully", "data": sale_receipt_serializer.data}, status=status.HTTP_201_CREATED)
