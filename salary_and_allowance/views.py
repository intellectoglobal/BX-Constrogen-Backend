from .models import SalaryAndAllowance
from buildiq.utils import UtilFunctions
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import SalaryAndAllowanceSerializer
from buildiq.pagenation_configs import Pagination10PerPage


class SalaryAndAllowanceViewSet(viewsets.ModelViewSet):
    queryset = SalaryAndAllowance.objects.all()
    serializer_class = SalaryAndAllowanceSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        filters = {
            'client_id': clientID,
            'company_id': companyID
        }

        year = request.GET.get("year")
        month = request.GET.get("month")
        if year and month:
            filters['date__year'] = year
            filters['date__month'] = month

        type_param = request.GET.get("type")
        if type_param:
            filters['type'] = 'S' if type_param == 'salary' else 'A'

        qrySet = self.queryset.filter(**filters).order_by('-key')

        # Handle without_pagination = 1
        if request.GET.get("without_pagination") and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(
                client_id=clientID,
                company_id=companyID,
                key=pk
            )
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"Salary And Allowance with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SalaryAndAllowanceSerializer(qrySet, many=False)
        return Response(serializer.data)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])


        req_data = request.data
        req_data['created_by'] = UF.getCurrentSessionUser(request)
        req_data['client_id'] = clientID
        req_data['company_id'] = companyID
        serializer = SalaryAndAllowanceSerializer(
            data=req_data)

        if serializer.is_valid():
            serializer.save()

        else:
            return Response({"error": 1, "detail": "Error in Salary And Allowance data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 0, "detail": "Salary And Allowance Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            bank_acc = SalaryAndAllowance.objects.get(key=pk)
        except SalaryAndAllowance.DoesNotExist:
            return Response({"error": 1, "detail": "Salary And Allowance does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['client_id'] = clientID
        bank_acc_serializer = SalaryAndAllowanceSerializer(
            instance=bank_acc, data=req_data, partial=True)

        if bank_acc_serializer.is_valid():
            bank_acc_serializer.save()
            return Response({"error": 0, "detail": "Salary And Allowance Updated Successfully", "data": bank_acc_serializer.data}, status=status.HTTP_200_OK)

        else:
            return Response({"error": 1, "detail": "Error in Salary And Allowance data", "data": bank_acc_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        SalaryAndAllowance_obj = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID,
            key=pk,
        )).delete()

        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)
