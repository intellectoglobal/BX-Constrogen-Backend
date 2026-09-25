from django.shortcuts import render
from .models import Clientbase, Company, Costcategory, Costcode, BankAccount
from .serializers import ClientBaseSerializer, CompanySerializer, CostcategorySerializer, CostcodeSerializer, BankAccountSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from buildiq.utils import UtilFunctions
from datetime import datetime
from buildiq.pagenation_configs import Pagination10PerPage
from project.models import Projectstatus
from project.serializers import ProjectStatusSerializer


class ClinetBaseViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Clientbase.objects.all()
    forbidenResponse = Response({"error": 1, "detail": "Access Denied", "data": {
    }}, status=status.HTTP_403_FORBIDDEN)
    UF = UtilFunctions()

    def list(self, request):
        if (not self.UF.isSuperAdmin(request)):
            return self.forbidenResponse

        serializer_class = ClientBaseSerializer(self.queryset.all(), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        if (self.UF.isSuperAdmin(request)):
            client = get_object_or_404(self.queryset, pk=pk)
        else:
            isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
                request)
            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])
            client = get_object_or_404(
                self.queryset.filter(id=clientID), pk=pk)

        serializer_class = ClientBaseSerializer(client)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        if (not self.UF.isSuperAdmin(request)):
            return self.forbidenResponse

        client = get_object_or_404(self.queryset, pk=pk)

        serializer = ClientBaseSerializer(
            client, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Client Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Client PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Client PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        if (not self.UF.isSuperAdmin(request)):
            return self.forbidenResponse

        request.data['id'] = Clientbase.nextID()
        serializer = ClientBaseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                client = serializer.save()
                if client:
                    return Response({"error": 0, "detail": "Client Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Client"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CompanyViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Company.objects.all()
    forbidenResponse = Response({"error": 1, "detail": "Access Denied", "data": {
    }}, status=status.HTTP_403_FORBIDDEN)
    UF = UtilFunctions()

    def list(self, request):
        if (not self.UF.isAuthenticatedUser(request)):
            return self.forbidenResponse
        
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = CompanySerializer(
            self.queryset.filter(client=clientID), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        if (self.UF.isSuperAdmin(request)):
            company = get_object_or_404(self.queryset, pk=pk)
        else:
            isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
                request)
            if not isValid:
                return Response(returnObj['message'], status=returnObj['http_status'])
            company = get_object_or_404(self.queryset.filter(
                id=companyID, client=clientID), pk=pk)

        serializer_class = CompanySerializer(company)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        if (not self.UF.isSuperAdmin(request)):
            return self.forbidenResponse

        company = get_object_or_404(self.queryset, pk=pk)

        serializer = CompanySerializer(
            company, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                for statusData in request.data.get('project_status', []):
                    projectStatus = {
                        'descr': statusData.get('descr', ''),
                        'is_active': statusData.get('is_active', False),
                        'company': company.id,
                        'client_id': company.client.id,
                    }
                    if Projectstatus.objects.filter(key=statusData.get('key')).exists():
                        projectStatusInstance = get_object_or_404(
                            Projectstatus, pk=statusData.get('key'))
                        proj_status_serializer = ProjectStatusSerializer(
                            projectStatusInstance, data=projectStatus, partial=True)
                        if proj_status_serializer.is_valid():
                            proj_status_serializer.save()
                    else:
                        proj_status_serializer = ProjectStatusSerializer(
                            data=projectStatus)
                        if proj_status_serializer.is_valid():
                            proj_status_serializer.save()

                return Response({"error": 0, "detail": "Company Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Company PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Company PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        if (not self.UF.isSuperAdmin(request)):
            return self.forbidenResponse

        request.data['id'] = Company().nextID()
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            try:
                company = serializer.save()
                if company:

                    for projStatusData in request.data.get('project_status', []):
                        statusData = {
                            'descr': projStatusData.get('descr', ''),
                            'is_active': projStatusData.get('is_active', False),
                            'company': company.id,
                            'client_id': company.client.id,
                        }
                        proj_status_serializer = ProjectStatusSerializer(
                            data=statusData)

                        if proj_status_serializer.is_valid():
                            proj_status_serializer.save()

                    return Response({"error": 0, "detail": "Company Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Company"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CostCategoryViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]

    queryset = Costcategory.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = CostcategorySerializer
    UF = UtilFunctions()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company=companyID, client_id=clientID).order_by('-key'))
        serializer = CostcategorySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        costCatIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = CostcategorySerializer(costCatIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        costCatIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)

        costCatIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        costCatIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = self.UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = CostcategorySerializer(
            costCatIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Cost Category Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Cost Category PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Cost Category PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = self.UF.getCurrentSessionUser(request)
        serializer = CostcategorySerializer(data=reqData)
        if serializer.is_valid():
            try:
                costCatIns = serializer.save()
                if costCatIns:
                    return Response({"error": 0, "detail": "Cost Category Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Cost Category"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CostCodeViewset(viewsets.GenericViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Costcode.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = CostcodeSerializer
    UF = UtilFunctions()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        page = self.paginate_queryset(self.queryset.filter(
            company=companyID, client_id=clientID).order_by('-key'))
        serializer = CostcodeSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        costCodeIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        serializer_class = CostcodeSerializer(costCodeIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        costCodeIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)
        costCodeIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = self.UF.getClientInfo(
            request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        costCodeIns = get_object_or_404(self.queryset.filter(
            company=companyID, client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = self.UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = CostcodeSerializer(
            costCodeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Cost Code Updated Successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Cost Code PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Cost Code PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = self.UF.getCurrentSessionUser(request)
        serializer = CostcodeSerializer(data=reqData)
        if serializer.is_valid():
            try:
                costCodeIns = serializer.save()
                if costCodeIns:
                    return Response({"error": 0, "detail": "Cost Code Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Cost Code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class BankAccountView(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID, company_id=companyID).order_by('-key')
        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = self.serializer_class(qrySet, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = BankAccountSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = BankAccountSerializer(qrySet, many=True)
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
                {'error': 1, "detail": f"BankAccount with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BankAccountSerializer(qrySet, many=False)
        return Response(serializer.data)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        req_data = request.data
        req_data['client_id'] = clientID
        req_data['company_id'] = companyID
        serializer = BankAccountSerializer(
            data=req_data)

        if serializer.is_valid():
            serializer.save()

        else:
            return Response({"error": 1, "detail": "Error in BankAccount data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 0, "detail": "BankAccount Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            bank_acc = BankAccount.objects.get(key=pk)
        except BankAccount.DoesNotExist:
            return Response({"error": 1, "detail": "BankAccount does not exist"}, status=status.HTTP_404_NOT_FOUND)

        req_data = request.data
        req_data['client_id'] = clientID
        bank_acc_serializer = BankAccountSerializer(
            instance=bank_acc, data=req_data, partial=True)

        if bank_acc_serializer.is_valid():
            bank_acc_serializer.save()
            return Response({"error": 0, "detail": "BankAccount Updated Successfully", "data": bank_acc_serializer.data}, status=status.HTTP_200_OK)

        else:
            return Response({"error": 1, "detail": "Error in BankAccount data", "data": bank_acc_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        BankAccount_obj = get_object_or_404(self.queryset.filter(
            client_id=clientID,
            company_id=companyID,
            key=pk,
        )).delete()

        return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)
