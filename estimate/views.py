from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from buildiq.pagenation_configs import Pagination10PerPage
from buildiq.utils import UtilFunctions
from django.shortcuts import get_object_or_404
from .models import WorkCategory, WorkType, WorkActivity
from .serializers import WorkCategorySerializer, WorkTypeSerializer, WorkActivitySerializer


class WorkCategoryViewset(viewsets.GenericViewSet):
    queryset = WorkCategory.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = WorkCategorySerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = WorkCategorySerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = WorkCategorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkCategoryIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = WorkCategorySerializer(WorkCategoryIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkCategoryIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodified_by'] = UF.getCurrentSessionUser(request)

        serializer = WorkCategorySerializer(
            WorkCategoryIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "WorkCategory Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error In WorkCategory PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": f"Error In WorkCategory PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkCategoryIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        WorkCategoryIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        reqData['created_by'] = UF.getCurrentSessionUser(request)
        reqData['client_id'] = clientID
        serializer = WorkCategorySerializer(data=reqData)
        if serializer.is_valid():
            try:
                WorkCategoryIns = serializer.save()
                if WorkCategoryIns:
                    return Response({"error": 0, "detail": "WorkCategory Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error While Adding WorkCategory: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": f"Error in API request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)


class WorkTypeViewset(viewsets.GenericViewSet):
    queryset = WorkType.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = WorkTypeSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if request.GET.get("category"):
            qrySet = self.queryset.filter(
                category_key=request.GET.get("category"))

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = WorkTypeSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = WorkTypeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = WorkTypeSerializer(WorkTypeIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodified_by'] = UF.getCurrentSessionUser(request)

        serializer = WorkTypeSerializer(
            WorkTypeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "WorkType Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error In WorkType PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": f"Error In WorkType PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkTypeIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        WorkTypeIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        reqData['created_by'] = UF.getCurrentSessionUser(request)
        reqData['client_id'] = clientID
        serializer = WorkTypeSerializer(data=reqData)
        if serializer.is_valid():
            try:
                WorkTypeIns = serializer.save()
                if WorkTypeIns:
                    return Response({"error": 0, "detail": "WorkType Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error While Adding WorkType: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": f"Error in API request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)


class WorkActivityViewset(viewsets.GenericViewSet):
    queryset = WorkActivity.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = WorkActivitySerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        category = request.GET.get("category")
        type  = request.GET.get("type")

        if category and type:
            qrySet = self.queryset.filter(
                category_key=category, type_key = type)

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = WorkActivitySerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = WorkActivitySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkActivityIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = WorkActivitySerializer(WorkActivityIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkActivityIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodified_by'] = UF.getCurrentSessionUser(request)

        serializer = WorkActivitySerializer(
            WorkActivityIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "WorkActivity Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error In WorkActivity PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": f"Error In WorkActivity PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        WorkActivityIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        WorkActivityIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        reqData['created_by'] = UF.getCurrentSessionUser(request)
        reqData['client_id'] = clientID
        serializer = WorkActivitySerializer(data=reqData)
        if serializer.is_valid():
            try:
                WorkActivityIns = serializer.save()
                if WorkActivityIns:
                    return Response({"error": 0, "detail": "WorkActivity Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": f"Error While Adding WorkActivity: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": f"Error in API request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
