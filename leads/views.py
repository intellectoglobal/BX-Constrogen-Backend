from datetime import datetime
from django.db import transaction
from buildiq.utils import UtilFunctions
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.db.models import Max, Subquery, OuterRef, Q
from buildiq.pagenation_configs import Pagination10PerPage
from project.models import Projectunit, Project, Projectstatus
from .models import LeadStatus, Lead, VisitStatus, Visit, FollowUpStatus, FollowUp, Comments, LeadSourceCategory,LeadSource,BudgetRanges,ProjectInterests,FloorPreference,FacingPreference,FollowUpStages,Occupancies,OccupancySubTypes,LocationPreference,LeadLocationPreference,LeadProjectPreference,LeadFacingPreference,FeedBack,FeedBackDetails
from client.models import Company, Clientbase
from .serializers import LeadStatusSerializer, LeadSerializer, VisitStatusSerializer, VisitSerializer, FollowUpStatusSerializer, FollowUpSerializer, LeadDetailSerializer, CommentsSerializer, PropertiesSerializer, ExportReportSerializer, LeadSourceCategorySerializer,LeadSourceSerializer,BudgetRangesSerializer,ProjectInterestsSerializer,FloorPrefSerializer,FacingPrefSerializer,FollowUpStagesSerializer,OccupanciesSerializer,LocationPreferenceSerializer,OccupancySubTypesSerializer,LeadLocationPreferenceSerializer,LeadProjectPreferenceSerializer,LeadFacingPreferenceSerializer,FeedbackSerializer,FeedbackDetailsSerializer, JunkLeadsSerializer, LeadProjectSerializer
from datetime import date


def _apply_contact_filter(queryset, contact_field, contact_value):
    contact_value = (contact_value or "").strip()
    if not contact_value:
        return queryset

    return queryset.filter(**{f"{contact_field}__icontains": contact_value})


def _create_lead_preferences(lead, req_data, clientID, companyID):
    warnings = []

    for pref in req_data.get("location_pref_keys", []):
        pref_value = pref.get("location_pref_key")
        if not pref_value:
            warnings.append("Lead location preferences were not saved.")
            continue

        serializer = LeadLocationPreferenceSerializer(data={
            'locationpref_key': pref_value,
            'lead_key': lead.key,
            'company': companyID,
            'client_id': clientID
        })
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                warnings.append("Lead location preferences were not saved.")
        else:
            warnings.append("Lead location preferences were not saved.")

    for pref in req_data.get("facing_pref_keys", []):
        pref_value = pref.get("facing_pref_key")
        if not pref_value:
            warnings.append("Lead facing preferences were not saved.")
            continue

        serializer = LeadFacingPreferenceSerializer(data={
            'facingpref_key': pref_value,
            'lead_key': lead.key,
            'company': companyID,
            'client_id': clientID
        })
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                warnings.append("Lead facing preferences were not saved.")
        else:
            warnings.append("Lead facing preferences were not saved.")

    for pref in req_data.get("project_pref_keys", []):
        pref_value = pref.get("project_pref_key")
        if not pref_value:
            warnings.append("Lead project preferences were not saved.")
            continue

        serializer = LeadProjectPreferenceSerializer(data={
            'project_key': pref_value,
            'lead_key': lead.key,
            'company': companyID,
            'client_id': clientID
        })
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                warnings.append("Lead project preferences were not saved.")
        else:
            warnings.append("Lead project preferences were not saved.")

    return list(dict.fromkeys(warnings))


class LeadDashboardViewset(viewsets.ViewSet):

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        today = date.today()

        total_leads = Lead.objects.filter(client_id=clientID, company_id=companyID).count()

        active_properties = Projectunit.objects.filter(
            client_id=clientID,
            company=companyID,
            projunit_status_key__descr='Available'
        ).count()
        
        total_visits = Visit.objects.filter(client_id=clientID, company_id=companyID).count()

        today_followups = FollowUp.objects.filter(
            client_id=clientID,
            company_id=companyID,
            last_followup_date=today,
            lead_key__status_key__name__in=['Hot', 'Warm']
        )

        today_site_visits = Visit.objects.filter(
            client_id=clientID,
            company_id=companyID,
            visit_date=today,
            lead_key__status_key__name__in=['Hot', 'Warm']
        )

        followup_data = FollowUpSerializer(today_followups, many=True).data
        sorted_followup_data = sorted(
            followup_data,
            key=lambda x: 0 if x['lead_status'] == 'Hot' else 1
        )

        visit_data = VisitSerializer(today_site_visits, many=True).data
        sorted_visit_data = sorted(
            visit_data,
            key=lambda x: 0 if x['lead_status'] == 'Hot' else 1
        )

        data = {
            "total_leads": total_leads,
            "active_properties": active_properties,
            "visits": total_visits,
            "conversion_rate": None,
            "today_followups": sorted_followup_data,
            "today_site_visits": sorted_visit_data,
        }

        return Response(data)


class LeadStatusViewset(viewsets.ViewSet):
    queryset = LeadStatus.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('name')
        serializer = LeadStatusSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = LeadStatusSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = LeadStatusSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Lead status Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Lead status PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Lead status PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = LeadStatusSerializer(data=request.data)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Lead Status Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Lead Status", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LeadProjectAllViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Project.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = LeadProjectSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        closedStatusList = Projectstatus.objects.filter(
            is_active=False,
            client_id=clientID,
            # company=companyID,
        ).values_list('key', flat=True)

        if len(closedStatusList) > 0:
            serialisedData = LeadProjectSerializer(
                self.queryset.filter(
                    client_id=clientID,
                    # company=companyID,
                ).filter(
                    ~Q(projstatus_key__in=closedStatusList)
                ).order_by('name'),
                many=True,
                read_only=True,
                fields=('key', 'id', 'name')
            ).data
        else:  # if the closed status not there in project status table
            serialisedData = LeadProjectSerializer(
                self.queryset.filter(
                    client_id=clientID,
                    # company=companyID,
                ).order_by('name'), many=True,
                read_only=True,
                fields=('key', 'id', 'name')
            ).data

        return Response(serialisedData)

class LeadSourceCategoryViewset(viewsets.ViewSet):
    queryset = LeadSourceCategory.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = LeadSourceCategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = LeadSourceCategorySerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = LeadSourceCategorySerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Lead Source Category Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Lead Source Category PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Lead Source Category PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = LeadSourceCategorySerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Lead Source Category Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Lead Source Category", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LeadSourceViewset(viewsets.ViewSet):
    queryset = LeadSource.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = LeadSourceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = LeadSourceSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = LeadSourceSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Lead Source Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Lead Source PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Lead Source PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = LeadSourceSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Lead Source Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Lead Source", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class BudgetRangesViewset(viewsets.ViewSet):
    queryset = BudgetRanges.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = BudgetRangesSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = BudgetRangesSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = BudgetRangesSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Budget Rangese Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Budget Ranges PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Budget Ranges PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = BudgetRangesSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Budget Ranges Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Budget Ranges", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectInterestsViewset(viewsets.ViewSet):
    queryset = ProjectInterests.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = ProjectInterestsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = ProjectInterestsSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset, pk=pk)
        serializer = ProjectInterestsSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Interests Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({"error": 1, "detail": "Error In Project Interests PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Interests PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = ProjectInterestsSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Project Interests Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Project Interests", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FloorsViewset(viewsets.ViewSet):
    queryset = FloorPreference.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = FloorPrefSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = FloorPrefSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = FloorPrefSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "FloorPreference Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In FloorPreference PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In FloorPreference PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = FloorPrefSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "FloorPreference Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding FloorPreference", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FacingViewset(viewsets.ViewSet):
    queryset = FacingPreference.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = FacingPrefSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = FacingPrefSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset, pk=pk)
        serializer = FacingPrefSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "FacingPreference Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({"error": 1, "detail": "Error In FacingPreference PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In FacingPreference PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = FacingPrefSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "FacingPreference Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding FacingPreference", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FollowUpStagesViewset(viewsets.ViewSet):
    queryset = FollowUpStages.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = FollowUpStagesSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = FollowUpStagesSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = FollowUpStagesSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "FollowUp Stages Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In FollowUp Stages PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In FollowUp Stages PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = FollowUpStagesSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "FollowUp Stages Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding FollowUp Stages", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OccupanciesViewset(viewsets.ViewSet):
    queryset = Occupancies.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = OccupanciesSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = OccupanciesSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = OccupanciesSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Occupancies Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Occupancies PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Occupancies PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = OccupanciesSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Occupancies Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Occupancies", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class OccupancySubTypesViewset(viewsets.ViewSet):
    queryset = OccupancySubTypes.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = OccupancySubTypesSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = OccupancySubTypesSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = OccupancySubTypesSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Occupancy Sub Types Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Occupancy Sub Types PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Occupancy Sub Types PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj,client_id,company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = OccupancySubTypesSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Occupancy Sub Types Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Occupancy Sub Types", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LocationPreferenceViewset(viewsets.ViewSet):
    queryset = LocationPreference.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = LocationPreferenceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = LocationPreferenceSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        # This method only updates LocationPreference master records
        # Lead location preference mappings are handled in LeadViewSet.update
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        locationIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = LocationPreferenceSerializer(
            locationIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Location Preference Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({"error": 1, "detail": "Error In Location Preference PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Location Preference PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, company_id, client_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = LocationPreferenceSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Location Preference Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Location Preference", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LeadViewset(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = LeadSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-enquiry_date','-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = LeadSerializer(
                qrySet, many=True, fields=('key', 'name'))
            data = {
                'queryset': serializer.data
            }
            return Response(data)

        if request.GET.get("status", False) and UF.isNum(request.GET.get("status")):
            qrySet = qrySet.filter(
                status_key=request.GET.get("status"))

        lead_name = request.GET.get("lead_name")
        if lead_name:
            qrySet = qrySet.filter(lead_name__icontains=lead_name)

        contact_1 = request.GET.get("contact_1")
        qrySet = _apply_contact_filter(qrySet, "contact_1", contact_1)

        active_followup = request.GET.get("active_followup")
        if active_followup in ["true", "True", "1"]:
            open_status_keys = LeadStatus.objects.filter(
                name__in=["Open", "Potential", "Re-Open"],
                client_id=clientID,
                company_id=companyID
            ).values_list("key", flat=True)
            qrySet = qrySet.filter(status_key__in=open_status_keys)

        page = self.paginate_queryset(qrySet)
        serializer = LeadSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        lead = get_object_or_404(
            self.queryset.filter(
                company_id=companyID,
                client_id=clientID
            ), pk=pk
        )

        serializer = LeadDetailSerializer(lead)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        lead = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        lead.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        leadInstance = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data.copy()
        location_prefs = reqData.pop('location_pref_keys', None)
        facing_prefs = reqData.pop('facing_pref_keys', None)
        project_prefs = reqData.pop('project_pref_keys', None)
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = LeadSerializer(
            leadInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    lead = serializer.save()

                    # Only touch preferences when the field is explicitly sent.
                    if location_prefs is not None:
                        LeadLocationPreference.objects.filter(lead_key=lead).delete()
                        processedKeys = []
                        for locpref in location_prefs:
                            locpref_data = {
                                'locationpref_key': locpref['location_pref_key'],
                                'lead_key': lead.key,
                                'company': companyID,
                                'client_id': clientID
                            }

                            pref_serializer = LeadLocationPreferenceSerializer(data=locpref_data)
                            if pref_serializer.is_valid():
                                pref_instance = pref_serializer.save()
                                processedKeys.append(pref_instance.key)
                            else:
                                LeadLocationPreference.objects.filter(key__in=processedKeys).delete()
                                raise Exception("Error updating location preferences")

                    if facing_prefs is not None:
                        LeadFacingPreference.objects.filter(lead_key=lead).delete()
                        processedFacingKeys = []
                        for facingpref in facing_prefs:
                            facingpref_data = {
                                'facingpref_key': facingpref['facing_pref_key'],
                                'lead_key': lead.key,
                                'company': companyID,
                                'client_id': clientID
                            }

                            pref_serializer = LeadFacingPreferenceSerializer(data=facingpref_data)
                            if pref_serializer.is_valid():
                                pref_instance = pref_serializer.save()
                                processedFacingKeys.append(pref_instance.key)
                            else:
                                LeadFacingPreference.objects.filter(key__in=processedFacingKeys).delete()
                                raise Exception("Error updating facing preferences")

                    if project_prefs is not None:
                        LeadProjectPreference.objects.filter(lead_key=lead).delete()
                        processedPropKeys = []
                        for proj_pref in project_prefs:
                            propref_data = {
                                'project_key': proj_pref['project_pref_key'],
                                'lead_key': lead.key,
                                'company': companyID,
                                'client_id': clientID
                            }

                            pref_serializer = LeadProjectPreferenceSerializer(data=propref_data)
                            if pref_serializer.is_valid():
                                pref_instance = pref_serializer.save()
                                processedPropKeys.append(pref_instance.key)
                            else:
                                LeadProjectPreference.objects.filter(key__in=processedPropKeys).delete()
                                raise Exception("Error updating project preferences")

                    return Response({"error": 0, "detail": "Lead Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": 1, "detail": f"Error In Lead PUT Request: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Lead PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data.copy()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = clientID
        reqData['company_id'] = companyID

        try:
            with transaction.atomic():
                reqData['lead_no'] = str(UF.getValidDocId(
                    reqData.get('lead_no'),
                    "LD",
                    clientID
                ))
                lead_serializer = LeadSerializer(data=reqData)
                if not lead_serializer.is_valid():
                    raise serializers.ValidationError(lead_serializer.errors)
                lead = lead_serializer.save()

            warnings = _create_lead_preferences(lead, reqData, clientID, companyID)
            response_data = LeadSerializer(lead).data
            detail = "Lead Added Successfully"
            if warnings:
                detail = "Lead Added Successfully. Some preferences were not saved."
                response_data["warnings"] = warnings

            return Response({"error": 0, "detail": detail, "data": response_data}, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"error": 1, "detail": "Error in API request", "data": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": 1, "detail": f"Error While Adding Lead: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class Contact1AvailabilityViewSet(viewsets.ViewSet):
    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        contact_1 = (request.GET.get("contact_1") or "").strip()
        exclude_lead_key = request.GET.get("exclude_lead_key")

        if not contact_1:
            return Response({
                "error": 1,
                "detail": "contact_1 query parameter is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        qrySet = Lead.objects.filter(
            company_id=companyID,
            client_id=clientID,
            contact_1=contact_1
        )

        if exclude_lead_key and UF.isNum(exclude_lead_key):
            qrySet = qrySet.exclude(pk=int(exclude_lead_key))

        existing_lead = qrySet.first()
        if existing_lead:
            return Response({
                "exists": True,
                "lead_key": existing_lead.key,
                "lead_name": existing_lead.lead_name,
                "message": f'Number already associated with "{existing_lead.lead_name or "Lead"}"'
            }, status=status.HTTP_200_OK)

        return Response({
            "exists": False,
            "message": "Contact number is available"
        }, status=status.HTTP_200_OK)


class VisitStatusViewset(viewsets.ViewSet):
    queryset = VisitStatus.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-name')
        serializer = VisitStatusSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = VisitStatusSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = VisitStatusSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Visit status Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Visit status PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Visit status PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = VisitStatusSerializer(data=request.data)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Visit Status Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Lead Status", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VisitViewset(viewsets.ModelViewSet):
    queryset = Visit.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = VisitSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        base_qs = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key')

        status = request.GET.get("status")
        if status and UF.isNum(status):
            base_qs = base_qs.filter(status_key=status)

        visit_date = request.GET.get("date")
        if visit_date:
            try:
                parsed_date = datetime.strptime(visit_date, "%d-%m-%Y").date()
                base_qs = base_qs.filter(visit_date=parsed_date)
            except ValueError:
                return Response({"error": "Invalid date format. Use dd-mm-yyyy."}, status=400)

        project = request.GET.get("project")
        if project and UF.isNum(project):
            base_qs = base_qs.filter(lead_key=project)

        lead_name = request.GET.get("lead_name")
        if lead_name:
            base_qs = base_qs.filter(lead_key__lead_name__icontains=lead_name)

        contact_1 = request.GET.get("contact_1")
        base_qs = _apply_contact_filter(base_qs, "lead_key__contact_1", contact_1)

        # Only latest site visit per lead (by visit_date, then key)
        latest_key_subquery = Visit.objects.filter(
            client_id=clientID,
            company_id=companyID,
            lead_key=OuterRef('lead_key'),
        ).order_by('-visit_date', '-key').values('key')[:1]
        qrySet = base_qs.filter(key=Subquery(latest_key_subquery))

        if request.GET.get("without_pagination") and int(request.GET.get("without_pagination")) == 1:
            serializer = VisitSerializer(
                qrySet, many=True, fields=('key', 'name'))
            data = {'queryset': serializer.data}
            return Response(data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = VisitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        visit = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = VisitSerializer(visit)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        visit = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        visit.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        visitInstance = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = VisitSerializer(
            visitInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Visit Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Visit PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Visit PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        serializer = VisitSerializer(data=reqData)
        if serializer.is_valid():
            try:
                visit = serializer.save()
                if visit:
                    return Response({"error": 0, "detail": "Visit Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Visit"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FollowUpStatusViewset(viewsets.ViewSet):
    queryset = FollowUpStatus.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('name')
        serializer = FollowUpStatusSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = FollowUpStatusSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        statusIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = FollowUpStatusSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "FollowUp status Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In FollowUp status PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In FollowUp status PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = FollowUpStatusSerializer(data=request.data)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "FollowUp Status Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding FollowUp Status", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FollowUpViewset(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = FollowUpSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        base_qs = self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ).order_by('-key')

        status = request.GET.get("status")
        if status and UF.isNum(status):
            base_qs = base_qs.filter(status_key=status)

        followup_date = request.GET.get("date")
        if followup_date:
            try:
                parsed_date = datetime.strptime(
                    followup_date, "%d-%m-%Y").date()
                base_qs = base_qs.filter(last_followup_date=parsed_date)
            except ValueError:
                return Response({"error": "Invalid date format. Use dd-mm-yyyy."}, status=400)

        project = request.GET.get("project")
        if project and UF.isNum(project):
            base_qs = base_qs.filter(lead_key=project)

        lead_name = request.GET.get("lead_name")
        if lead_name:
            base_qs = base_qs.filter(lead_key__lead_name__icontains=lead_name)

        contact_1 = request.GET.get("contact_1")
        base_qs = _apply_contact_filter(base_qs, "lead_key__contact_1", contact_1)

        # Only latest followup per lead (by date, then key)
        latest_key_subquery = FollowUp.objects.filter(
            client_id=clientID,
            company_id=companyID,
            lead_key=OuterRef('lead_key'),
        ).order_by('-last_followup_date', '-key').values('key')[:1]
        qrySet = base_qs.filter(key=Subquery(latest_key_subquery))

        # Only include followups where latest feedback is "Follow-up" or "Un Answered calls"
        qrySet = qrySet.filter(
            feedback_key__descr__in=['Follow-up', 'Un Answered calls']
        )

        if request.GET.get("without_pagination") and int(request.GET.get("without_pagination")) == 1:
            serializer = FollowUpSerializer(
                qrySet, many=True, fields=('key', 'name'))
            data = {'queryset': serializer.data}
            return Response(data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = FollowUpSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        lead = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = FollowUpSerializer(lead)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        lead = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        lead.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        followUpInstance = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = FollowUpSerializer(
            followUpInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "FollowUp Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In FollowUp PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In FollowUp PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        serializer = FollowUpSerializer(data=reqData)
        if serializer.is_valid():
            try:
                follow_up = serializer.save()
                if follow_up:
                    return Response({"error": 0, "detail": "FollowUp Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding FollowUp"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LeadRelatedDataViewSet(viewsets.ViewSet):
    def list(self, request):
        # Fetch and return list of visits/followups as needed
        data = {
            "visit": list(Visit.objects.all().values()),
            "followup": list(FollowUp.objects.all().values()),
        }
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            lead = get_object_or_404(
                Lead, pk=pk, client_id=clientID, company_id=companyID)

            visits = Visit.objects.filter(
                lead_key=lead, client_id=clientID, company_id=companyID
            ).select_related('status_key', 'project_key')

            followups = FollowUp.objects.filter(
                lead_key=lead, client_id=clientID, company_id=companyID
            ).select_related('status_key')

            lead_data = LeadSerializer(lead).data
            visit_data = VisitSerializer(visits, many=True).data
            followup_data = FollowUpSerializer(followups, many=True).data

            response_data = {
                **lead_data,
                "visit": visit_data,
                "followup": followup_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        createdby = UF.getCurrentSessionUser(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            lead_key = reqData.get("key")
            if not lead_key:
                return Response({"error": 1, "detail": "Lead key is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate lead exists
            try:
                lead = Lead.objects.get(key=lead_key, client_id=clientID, company_id=companyID)
            except Lead.DoesNotExist:
                return Response({"error": 1, "detail": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)

            # Process visits with proper validation
            visit_errors = []
            visit_success_count = 0
            for idx, visit_data in enumerate(reqData.get("visit", [])):
                try:
                    # Get the first available project for this client/company as default
                    default_project = None
                    try:
                        from project.models import Project
                        default_project = Project.objects.filter(
                            client_id=clientID, company=companyID
                        ).first()
                    except:
                        pass

                    # Prepare visit data with required fields and defaults
                    visit_payload = {
                        'lead_key': lead_key,
                        'visit_date': parse_date(visit_data.get("visit_date")),
                        'visit_time': visit_data.get("visit_time", ""),
                        'project_key': visit_data.get("project_key") or (default_project.key if default_project else None),
                        'agent_name': visit_data.get("agent_name", "System Agent"),
                        'agent_phone': visit_data.get("agent_phone", "+0000000000"),
                        'status_key': visit_data.get("status_key"),
                        'createdby': createdby,
                        'client_id': clientID,
                        'company_id': companyID
                    }

                    # Validate required fields
                    if not visit_payload['project_key']:
                        visit_errors.append(f"Visit {idx+1}: No project available for this client/company")
                        continue

                    if not visit_payload['status_key']:
                        visit_errors.append(f"Visit {idx+1}: status_key is required")
                        continue

                    # Try direct object creation first (bypass serializer validation for testing)
                    try:
                        visit_obj = Visit.objects.create(**visit_payload)
                        visit_success_count += 1
                        print(f"Visit {idx+1} saved with ID: {visit_obj.key}")
                    except Exception as create_error:
                        visit_errors.append(f"Visit {idx+1} create failed: {str(create_error)}")
                        print(f"Visit {idx+1} create error: {str(create_error)}")

                except Exception as e:
                    visit_errors.append(f"Visit {idx+1}: {str(e)}")
                    print(f"Visit {idx+1} general error: {str(e)}")
                    import traceback
                    traceback.print_exc()

            # Process followups with proper validation
            followup_errors = []
            for idx, followup_data in enumerate(reqData.get("followup", [])):
                try:
                    followup_payload = {
                        'lead_key': lead_key,
                        'last_followup_date': parse_date(followup_data.get("last_followup_date")),
                        'followup_time': followup_data.get("followup_time", ""),
                        'follow_notes': followup_data.get("follow_notes", ""),
                        'status_key': followup_data.get("status_key"),
                        'feedback_key': followup_data.get("feedback_key"),
                        'followup_details_key': followup_data.get("followup_details_key"),
                        'createdby': createdby,
                        'client_id': clientID,
                        'company_id': companyID
                    }

                    # Use serializer for validation
                    serializer = FollowUpSerializer(data=followup_payload)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        followup_errors.append(f"FollowUp {idx+1}: {serializer.errors}")

                except Exception as e:
                    followup_errors.append(f"FollowUp {idx+1}: {str(e)}")

            # Check if there were any errors
            all_errors = visit_errors + followup_errors
            if all_errors:
                return Response({
                    "error": 1,
                    "detail": "Some records failed to save",
                    "errors": all_errors
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Visit and FollowUp created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": 1, "detail": f"Unexpected error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        modifiedby = UF.getCurrentSessionUser(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            incoming_followups = reqData.get("followup", [])

            existing_followups = FollowUp.objects.filter(
                lead_key=pk, client_id=clientID, company_id=companyID)

            incoming_followup_ids = [
                f.get("key") for f in incoming_followups if f.get("key")]

            existing_followups.exclude(pk__in=incoming_followup_ids).delete()

            for followup_data in incoming_followups:
                if "key" in followup_data:
                    followup = FollowUp.objects.get(
                        pk=followup_data["key"], lead_key=pk)
                    followup_data['lastmodifiedby'] = modifiedby
                    serializer = FollowUpSerializer(
                        followup, data=followup_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"error": 1, "detail": f"Error In Updating Existing FollowUp: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    followup_data["lead_key"] = pk
                    followup_data["createdby"] = modifiedby
                    followup_data["client_id"] = clientID
                    followup_data["company_id"] = companyID
                    serializer = FollowUpSerializer(data=followup_data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"error": 1, "detail": f"Error In Creating New FollowUp: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

            incoming_visits = reqData.get("visit", [])
            existing_visits = Visit.objects.filter(
                lead_key=pk, client_id=clientID, company_id=companyID)

            incoming_visit_ids = [v.get("key")
                                  for v in incoming_visits if v.get("key")]
            print("Incoming Visit IDs:", incoming_visit_ids)
            existing_visits.exclude(pk__in=incoming_visit_ids).delete()

            for visit_data in incoming_visits:
                if "key" in visit_data:
                    visit = Visit.objects.get(
                        pk=visit_data["key"], lead_key=pk)
                    visit_data['lastmodifiedby'] = modifiedby
                    serializer = VisitSerializer(
                        visit, data=visit_data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"error": 1, "detail": f"Error In Updating Existing Visit: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    visit_data["lead_key"] = pk
                    visit_data["createdby"] = modifiedby
                    visit_data["client_id"] = clientID
                    visit_data["company_id"] = companyID
                    serializer = VisitSerializer(data=visit_data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response({"error": 1, "detail": f"Error In Creating New Visit: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"error": 0, "detail": "Visit and FollowUp updated successfully."}, status=status.HTTP_200_OK)

        except Lead.DoesNotExist:
            return Response({"error": 1, "detail": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            # Delete related visits and followups
            Visit.objects.filter(
                lead_key=pk, client_id=clientID, company_id=companyID).delete()
            FollowUp.objects.filter(
                lead_key=pk, client_id=clientID, company_id=companyID).delete()

            return Response({"error": 0, "detail": "Related visits and followups deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CommentsViewSet(viewsets.ViewSet):
    serializer_class = CommentsSerializer

    def get_comment_type_from_path(self, request):
        if 'lead/comments' in request.path:
            return 'Lead'
        elif 'follow-up/comments' in request.path:
            return 'FollowUp'
        elif 'visit/comments' in request.path:
            return 'Visit'
        return None

    def retrieve(self, request, pk=None):
        comment_type = self.get_comment_type_from_path(request)
        queryset = Comments.objects.filter(
            related_key=pk, comment_type=comment_type)
        serializer = CommentsSerializer(queryset, many=True)
        return Response(serializer.data)

    @method_decorator(csrf_exempt)
    @transaction.atomic
    def update(self, request, pk=None):
        comment_type = self.get_comment_type_from_path(request)
        UF = UtilFunctions()
        user = UF.getCurrentSessionUser(request)
        related_key = pk
        created_comments = []
        new_comments = [comment for comment in request.data.get(
            'comments', []) if not comment.get('key')]
        for comment_data in new_comments:
            comment_data.update({
                "related_key": related_key,
                "comment_type": comment_type,
                "createdby": user,
            })
            serializer = CommentsSerializer(data=comment_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            created_comments.append(serializer.data)

        return Response(created_comments, status=status.HTTP_200_OK)


class PropertiesViewset(viewsets.ViewSet):
    queryset = Projectunit.objects.all()
    # queryset = Projectunit.objects.select_related('proj_key', 'projunit_status_key')
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = PropertiesSerializer(
            self.queryset.filter(
                company_id=companyID,
                client_id=clientID
            ), many=True)
        return Response(serializer_class.data)


class ExportReportViewset(viewsets.ViewSet):
    queryset = Lead.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        year = request.GET.get('year')
        month = request.GET.get('month')

        serializer_class = ExportReportSerializer(
            self.queryset.filter(
                company_id=companyID,
                client_id=clientID,
                enquiry_date__year = year,
                enquiry_date__month = month
            ), many=True)
        return Response(serializer_class.data)


class FeedBackViewset(viewsets.ViewSet):
    queryset = FeedBack.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).order_by('descr')
        serializer = FeedbackSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        feedbackIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = FeedbackSerializer(feedbackIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        feedbackIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        feedbackIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        feedbackIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = FeedbackSerializer(
            feedbackIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Feedback Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Feedback PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Feedback PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, company_id, client_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = FeedbackSerializer(data=reqData)
        if serializer.is_valid():

            try:
                feedbackIns = serializer.save()
                if feedbackIns:
                    return Response({"error": 0, "detail": "Feedback Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Feedback", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FeedBackDetailsViewset(viewsets.ViewSet):
    queryset = FeedBackDetails.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = self.queryset.filter(
            client_id=clientID
        ).select_related('feedback_id')

        feedback_key = request.GET.get('feedback_id')
        if feedback_key:
            queryset = queryset.filter(feedback_id=feedback_key)

        queryset = queryset.order_by('feedback_id__descr', 'descr')
        serializer = FeedbackDetailsSerializer(queryset, many=True)
        flat_data = serializer.data

        # Backward-compat mode for clients expecting the old flat array.
        if str(request.GET.get('flat', '0')) == '1':
            return Response(flat_data)

        grouped_details = {}
        for item in flat_data:
            fb_id = item.get('feedback_id')
            if not fb_id:
                continue

            if fb_id not in grouped_details:
                grouped_details[fb_id] = []
            grouped_details[fb_id].append({
                'key': item.get('key'),
                'descr': item.get('descr'),
                'client_id': item.get('client_id'),
                'feedback_id': fb_id,
            })

        feedbacks = FeedBack.objects.filter(
            client_id=clientID
        ).order_by('descr')
        if feedback_key:
            feedbacks = feedbacks.filter(key=feedback_key)

        response_data = []
        for feedback in feedbacks:
            response_data.append({
                'feedback': {
                    'key': feedback.key,
                    'descr': feedback.descr,
                },
                'feedback_details': grouped_details.get(feedback.key, []),
            })

        return Response(response_data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        feedbackDetailsIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = FeedbackDetailsSerializer(feedbackDetailsIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        feedbackDetailsIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        feedbackDetailsIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        feedbackDetailsIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer = FeedbackDetailsSerializer(
            feedbackDetailsIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Feedback Details Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Feedback Details PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Feedback Details PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, company_id, client_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        reqData['client_id'] = client_id

        serializer = FeedbackDetailsSerializer(data=reqData)
        if serializer.is_valid():

            try:
                feedbackDetailsIns = serializer.save()
                if feedbackDetailsIns:
                    return Response({"error": 0, "detail": "Feedback Details Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Feedback Details", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class JunkLeadsViewset(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = JunkLeadsSerializer

    def get_queryset(self):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(self.request)
        if not isValid:
            return FollowUp.objects.none()

        junk_feedbacks = FeedBack.objects.filter(
            client_id=clientID,
            descr__in=['Irrelevant call', 'Un Answered calls']
        ).values_list('key', flat=True)

        base_qs = FollowUp.objects.filter(
            client_id=clientID,
            company_id=companyID
        )
        latest_key_subquery = FollowUp.objects.filter(
            client_id=clientID,
            company_id=companyID,
            lead_key=OuterRef('lead_key'),
        ).order_by('-last_followup_date', '-key').values('key')[:1]
        return base_qs.filter(
            key=Subquery(latest_key_subquery),
            feedback_key__in=junk_feedbacks
        )

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        # Filter for Junk leads based on FollowUp feedback
        # Get feedback IDs for "Irrelevant call" and "Un Answered calls"
        junk_feedbacks = FeedBack.objects.filter(
            client_id=clientID,
            descr__in=['Irrelevant call', 'Un Answered calls']
        ).values_list('key', flat=True)

        # Get leads that have followups with junk feedback
        base_qs = FollowUp.objects.filter(
            client_id=clientID,
            company_id=companyID
        )
        latest_key_subquery = FollowUp.objects.filter(
            client_id=clientID,
            company_id=companyID,
            lead_key=OuterRef('lead_key'),
        ).order_by('-last_followup_date', '-key').values('key')[:1]
        qrySet = base_qs.filter(
            key=Subquery(latest_key_subquery),
            feedback_key__in=junk_feedbacks
        )

        # Apply additional filters if provided
        lead_name = request.GET.get("lead_name")
        if lead_name:
            qrySet = qrySet.filter(lead_key__lead_name__icontains=lead_name)

        contact_1 = request.GET.get("contact_1")
        qrySet = _apply_contact_filter(qrySet, "lead_key__contact_1", contact_1)

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = JunkLeadsSerializer(qrySet, many=True)
            data = {
                'queryset': serializer.data
            }
            return Response(data)

        page = self.paginate_queryset(qrySet)
        serializer = JunkLeadsSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        print(" RETRIEVE HIT, pk =", pk)
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        # The pk parameter is a FollowUp key, not a Lead key
        try:
            junk_followup = FollowUp.objects.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except FollowUp.DoesNotExist:
            return Response({"error": "Junk lead followup not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if this followup qualifies as a junk lead
        junk_feedbacks = FeedBack.objects.filter(
            client_id=clientID,
            descr__in=['Irrelevant call', 'Un Answered calls']
        ).values_list('key', flat=True)

        if junk_followup.feedback_key.key not in junk_feedbacks:
            return Response({"error": "This followup is not marked as junk"}, status=status.HTTP_404_NOT_FOUND)

        serializer = JunkLeadsSerializer(junk_followup)
        return Response(serializer.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        # Get the FollowUp object directly
        try:
            junk_followup = FollowUp.objects.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except FollowUp.DoesNotExist:
            return Response({"error": "Junk lead followup not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate it's actually a junk lead
        junk_feedbacks = FeedBack.objects.filter(
            client_id=clientID,
            descr__in=['Irrelevant call', 'Un Answered calls']
        ).values_list('key', flat=True)

        if junk_followup.feedback_key.key not in junk_feedbacks:
            return Response({"error": "This followup is not marked as junk"}, status=status.HTTP_404_NOT_FOUND)

        reqData = request.data.copy()
        location_prefs = reqData.pop('location_pref_keys', None)
        project_prefs = reqData.pop('project_pref_keys', None)
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = JunkLeadsSerializer(
            junk_followup, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    followup = serializer.save()

                    # Handle location preferences: only delete and recreate if explicitly provided
                    if location_prefs is not None:
                        LeadLocationPreference.objects.filter(lead_key=followup.lead_key).delete()
                        processedKeys = []
                        for locpref in location_prefs:
                            locpref_data = {
                                'locationpref_key': locpref['location_pref_key'],
                                'lead_key': followup.lead_key.key,
                                'company': companyID,
                                'client_id': clientID
                            }

                            pref_serializer = LeadLocationPreferenceSerializer(data=locpref_data)
                            if pref_serializer.is_valid():
                                pref_instance = pref_serializer.save()
                                processedKeys.append(pref_instance.key)
                            else:
                                LeadLocationPreference.objects.filter(key__in=processedKeys).delete()
                                raise Exception("Error updating location preferences")

                    # Handle project preferences: only delete and recreate if explicitly provided
                    if project_prefs is not None:
                        LeadProjectPreference.objects.filter(lead_key=followup.lead_key).delete()
                        processedPropKeys = []
                        for proj_pref in project_prefs:
                            propref_data = {
                                'project_key': proj_pref['project_pref_key'],
                                'lead_key': followup.lead_key.key,
                                'company': companyID,
                                'client_id': clientID
                            }

                            pref_serializer = LeadProjectPreferenceSerializer(data=propref_data)
                            if pref_serializer.is_valid():
                                pref_instance = pref_serializer.save()
                                processedPropKeys.append(pref_instance.key)
                            else:
                                LeadProjectPreference.objects.filter(key__in=processedPropKeys).delete()
                                raise Exception("Error updating project preferences")

                    return Response({"error": 0, "detail": "Junk Lead Updated Successfully", "data": serializer.data}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": 1, "detail": f"Error In Junk Lead PUT Request: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Junk Lead PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
