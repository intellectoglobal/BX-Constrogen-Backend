from django.shortcuts import render
from .models import City, State
from .serializers import StateSerializer, CitySerializer
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from users.models import AppUser
from buildiq.utils import UtilFunctions
from datetime import datetime


class StateViewset(viewsets.ViewSet):
    queryset = State.objects.all()

    def list(self, request):
        serializer_class = StateSerializer(self.queryset.all().order_by('name'), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        state = get_object_or_404(self.queryset, pk=pk)
        serializer_class = StateSerializer(state)
        return Response(serializer_class.data)
    
    def delete(self, request, pk=None):
        cityIns = get_object_or_404(self.queryset, pk=pk)
        cityIns.delete()
        return Response("Delete Success")
    
    def update(self, request, pk=None):
        stateInstance = get_object_or_404(self.queryset, pk=pk)
        serializer = StateSerializer(
            stateInstance, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "State Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In State PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In State PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            if State.objects.filter(id=request.data["id"]).exists():
                return Response({"error": 1, "detail": "State Code Allready Exists"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                state = serializer.save()
                if state:
                    return Response({"error": 0, "detail": "State Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding State"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CityViewset(viewsets.ViewSet):
    queryset = City.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if request.GET.get('state', False) and not request.GET.get('state') == "":
            cityQrySet = self.queryset.filter(
                state_key=request.GET.get('state'),client_id=clientID, company=companyID).order_by('name')
        else:
            cityQrySet = self.queryset.filter(client_id=clientID, company=companyID).order_by('name')
        serializer_class = CitySerializer(cityQrySet, many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        city = get_object_or_404(self.queryset, pk=pk)
        serializer_class = CitySerializer(city)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        cityIns = get_object_or_404(self.queryset, pk=pk)
        cityIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        cityInstance = get_object_or_404(self.queryset, pk=pk)

        UF = UtilFunctions()
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = CitySerializer(
            cityInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "City Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In City PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In City PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = CitySerializer(data=reqData)
        if serializer.is_valid():
            try:
                city = serializer.save()
                if city:
                    return Response({"error": 0, "detail": "City Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding City", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
