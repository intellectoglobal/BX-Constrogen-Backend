from django.shortcuts import render
from .models import (Amenity, Projecttype, Projectstatus,
                     Project, Projcostcode, Projectamenity,
                     Projectblock, Projectfloor, ProjectUnitStatus, Projectunit, Projectstage,
                     Projpayterms, Projpricehistory, Projstatushistory,
                     Projecttask, ProjectWork, ProjectElevationDiagrams, Project3DFloorPlanHdr, Project3DFloorPlanDtl, PaidExpenses, ExpenseType, ExpenseVendor, ProjectSchedule)
from .serializers import (ProjectStatusSerializer, ProjectTypeSerializer,
                          ProjectSerializer, AmenitySerializer, ProjectAmenitySerializer, ProjCostCodeSerializer,
                          ProjectBlockSerializer, ProjectFloorSerializer, ProjectUnitStatusSerializer, ProjectUnitSerializer, ProjectStageSerializer,
                          ProjPayTermsSerializer, ProjPriceHistorySerializer, ProjStatusHistorySerializer,
                          ProjectTaskSerializer, ProjectWorkSerializer, ProjectElevationSerializer, Project3DFloorPlanHdrSerializer,
                          Project3DFloorPlanDtlSerializer, PaidExpensesSerializer, ExpenseTypeSerializer, ExpenseVendorSerializer,
                          ProjectScheduleSerializer)
from geolocation.models import City, State
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from datetime import datetime
from buildiq.utils import UtilFunctions
from buildiq.pagenation_configs import Pagination10PerPage
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
import io
import base64
import uuid


class ProjectStatusViewset(viewsets.ViewSet):
    queryset = Projectstatus.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qryset = self.queryset.filter(
            company=companyID,
            client_id=clientID
        ).order_by('descr')
        serializer = ProjectStatusSerializer(qryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = ProjectStatusSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company=companyID,
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
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = ProjectStatusSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project status Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project status PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project status PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = ProjectStatusSerializer(data=request.data)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Project Status Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Project Status", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectTypeViewset(viewsets.GenericViewSet):
    queryset = Projecttype.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectTypeSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID,
            company=companyID
        ).order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectTypeSerializer(
                qrySet, many=True, fields=('key', 'id', 'descr'))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet)
            serializer = ProjectTypeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        typeIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectTypeSerializer(typeIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        typeIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        typeIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTypeInstance = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        UF = UtilFunctions()
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectTypeSerializer(
            proTypeInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Type Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Type PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Type PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectTypeSerializer(data=reqData)
        if serializer.is_valid():
            try:
                typeIns = serializer.save()
                if typeIns:
                    return Response({"error": 0, "detail": "Project Type Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Type"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewset(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company=companyID,
            client_id=clientID
        ).order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectSerializer(
                qrySet, many=True, fields=('key', 'id', 'name'))
            data = {
                'queryset': serializer.data
            }
            return Response(data)
        else:
            if request.GET.get("status", False) and UF.isNum(request.GET.get("status")):
                qrySet = qrySet.filter(
                    projstatus_key=request.GET.get("status"))
            page = self.paginate_queryset(qrySet)
            serializer = ProjectSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectSerializer(project)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        project.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectInstance = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        if request.data.get("is_image_updated") == "true":
            if request.data.get("elevationimage", False) and not request.data.get("elevationimage") == "null":
                # changeing project image
                proImage = UF.updateImageToCloud(
                    request.data['elevationimage'],
                    "base64",
                    "project_cover_image"
                )
                if proImage == None:
                    return Response({"error": 1, "detail": "Fail to upload project image", "data": "Fail to upload project image"}, status=status.HTTP_400_BAD_REQUEST)
                reqData['elevationimage'] = proImage

            elif request.data.get("elevationimage", False) and request.data.get("elevationimage") == "null":
                # remove project image
                reqData['elevationimage'] = ""

        serializer = ProjectSerializer(
            projectInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        user = UF.getCurrentSessionUser(request)
        reqData['createdby'] = user

        # image upload
        if request.data.get('elevationimage', False):
            proImage = UF.updateImageToCloud(
                request.data['elevationimage'],
                "base64",
                "project_cover_image"
            )
            if proImage == None:
                return Response({"error": 1, "detail": "Fail to upload project image", "data": "Fail to upload project image"}, status=status.HTTP_400_BAD_REQUEST)
            reqData['elevationimage'] = proImage

        serializer = ProjectSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                block_data = {
                    "client_id": reqData.get("client_id"),
                    "company": reqData.get("company"),
                    "company_id": reqData.get("company_id"),
                    "company_name": reqData.get("company_name"),
                    "descr": reqData.get("descr", "Main"),
                    "proj_key": project.pk,
                    "id": Projectblock().nextID(),
                    "createdby": user
                }

                block_serializer = ProjectBlockSerializer(data=block_data)
                if block_serializer.is_valid():
                    block_serializer.save()
                else:
                    project.delete()
                    return Response({"error": 1, "detail": "Error in ProjectBlock creation", "data": block_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                if project:
                    return Response({"error": 0, "detail": "Project Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectElevationViewSet(viewsets.ModelViewSet):
    queryset = ProjectElevationDiagrams.objects.all()
    serializer_class = ProjectElevationSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project_id = request.GET.get("project_id", None)
        block_id = request.GET.get("block_id", None)

        if project_id is None or block_id is None:
            return Response({"error": 1, "detail": "Missing required fields in request data"}, status=status.HTTP_400_BAD_REQUEST)

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID,
            project_id=project_id,
            block_id=block_id
        ).order_by('-key')

        serializer = ProjectElevationSerializer(qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID,
            project_id=pk
        )

        serializer = ProjectElevationSerializer(qrySet, many=True)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        elelvation_image = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID,
            key=pk
        ))
        img_url = elelvation_image.image_url

        result = UF.delete_file_from_s3(img_url)
        if result['success'] == True:
            elelvation_image.delete()
            return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Error occured while deleting the image"}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        req_data = request.data

        files = req_data.get('files', [])
        client_id = req_data.get('client_id')
        company_id = req_data.get('company_id')
        project_id = req_data.get('proj_key')
        block_id = req_data.get('block_id')

        if not client_id or not company_id or not project_id or not block_id or not files:
            return Response({"error": 1, "detail": "Missing required fields in request data"}, status=status.HTTP_400_BAD_REQUEST)

        existing_image = ProjectElevationDiagrams.objects.filter(
            client_id=client_id, company_id=company_id, project_id=project_id, block_id=block_id).first()

        if existing_image:
            result = UF.delete_file_from_s3(existing_image.image_url)
            if result['success'] == True:
                try:
                    existing_image.delete()
                except Exception as e:
                    return Response({"error": 1, "detail": "Error occured while deleting existing image data in db"})
            else:
                return Response({"error": 1, "detail": "Error occured while deleting existing image"})

        folder_path = UF.create_s3_folder_structure(
            client_id, company_id, project_id, block_id)

        for file in files:
            try:
                header, base64_data = file.split(',', 1)
                decoded_file = base64.b64decode(base64_data)
                file_like = io.BytesIO(decoded_file)

                file_name = f"{uuid.uuid4()}.jpg"
                s3_path = f"{folder_path}/elevation/{file_name}"

                file_url = UF.upload_file_to_s3(s3_path, file_like)
                if not file_url:
                    return Response({"error": 1, "detail": "Failed to upload project elevation diagram"}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"error": 1, "detail": f"Invalid base64 image format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        elevation_data = {
            'image_url': file_url,
            'client_id': client_id,
            'company_id': company_id,
            'project_id': project_id,
            'block_id': block_id,
        }

        serializer = ProjectElevationSerializer(data=elevation_data)
        if serializer.is_valid():
            elevation = serializer.save()
            if elevation:
                return Response({"error": 0, "detail": "Project Elevation Diagram Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

        else:
            return Response({"error": 1, "detail": "Error in Uploading Project Elevation Diagram", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class Project3DFloorPlansViewSet(viewsets.ModelViewSet):
    queryset = Project3DFloorPlanHdr.objects.all()
    serializer_class = Project3DFloorPlanHdrSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project_id = request.GET.get("project", None)
        block_id = request.GET.get("block", None)

        if project_id is None or block_id is None:
            return Response({"error": 1, "detail": "Missing required fields in request data"}, status=status.HTTP_400_BAD_REQUEST)

        qrySet = self.queryset.filter(
            company_id=companyID,
            client_id=clientID,
            project_id=project_id,
            block_id=block_id
        ).order_by('-key')

        serializer = Project3DFloorPlanHdrSerializer(qrySet, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            qrySet = self.queryset.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except Project3DFloorPlanHdr.DoesNotExist:
            return Response({"error": 1, "detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = Project3DFloorPlanHdrSerializer(qrySet)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        project3d_floor_hdr = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID,
            key=pk
        ))

        img_url = project3d_floor_hdr.image_url

        result = UF.delete_file_from_s3(img_url)
        if result['success'] == True:
            project3d_floor_hdr.delete()
            return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Error occured while deleting the image"}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        UF = UtilFunctions()
        req_data = request.data

        isValid, returnObj, client_id, company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        files = req_data.get('files', [])
        image_type = req_data.get('image_type')
        image_name = req_data.get('image_name')
        project_id = req_data.get('proj_key')
        block_id = req_data.get('block_id')
        floor_ids = req_data.get('floor_ids')

        if not all([client_id, company_id, project_id, files, image_type, image_name, block_id, floor_ids]):
            return Response({"error": 1, "detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        folder_path = UF.create_s3_folder_structure(
            client_id, company_id, project_id, block_id, floor_ids)

        for file in files:
            try:
                if ',' not in file:
                    return Response({"error": 1, "detail": "Invalid file format"}, status=status.HTTP_400_BAD_REQUEST)

                header, base64_data = file.split(',', 1)
                decoded_file = base64.b64decode(base64_data)
                file_like = io.BytesIO(decoded_file)

                mime_type = header.split(';')[0].split(':')[1]
                ext_map = {
                    'application/pdf': 'pdf',
                    'image/jpeg': 'jpg',
                    'image/png': 'png'
                }
                file_ext = ext_map.get(mime_type)

                if not file_ext:
                    return Response({"error": 1, "detail": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

                file_name = f"{uuid.uuid4()}.{file_ext}"
                s3_folder = "3D" if image_type == "3D" else "floor_plan"
                s3_path = f"{folder_path}/{s3_folder}/{file_name}"

                file_url = UF.upload_file_to_s3(
                    s3_path, file_like, content_type=mime_type)
                if not file_url:
                    return Response({"error": 1, "detail": "Failed to upload file"}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"error": 1, "detail": f"File processing error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        hdr_data = {
            'image_type': image_type,
            'image_name': image_name,
            'image_url': file_url,
            'client_id': client_id,
            'company_id': company_id,
            'project_id': project_id,
            'block_id': block_id,
        }

        hdr_serializer = Project3DFloorPlanHdrSerializer(data=hdr_data)

        if hdr_serializer.is_valid():
            elevation = hdr_serializer.save()
            hdr_key = elevation.key

            for floor_id in floor_ids:
                dtl_data = {
                    "hdr_key": hdr_key,
                    "floor_id": floor_id

                }
                dtl_serializer = Project3DFloorPlanDtlSerializer(data=dtl_data)
                if dtl_serializer.is_valid():
                    dtl_serializer.save()

                else:
                    return Response({"error": 0, "detail": f"Error While Adding Image to Floor:  {dtl_serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": f"Error in Uploading Project 3D Floor Plan: {hdr_serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 0, "detail": "Project 3D Floor Plan Added Successfully", "data": hdr_serializer.data}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, pk=None):
        UF = UtilFunctions()
        req_data = request.data

        isValid, returnObj, client_id, company_id = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        files = req_data.get('files', [])
        image_type = req_data.get('image_type')
        image_name = req_data.get('image_name')
        project_id = req_data.get('proj_key')
        block_id = req_data.get('block_id')
        floor_ids = req_data.get('floor_ids')

        if not all([client_id, company_id, project_id, image_type, block_id, floor_ids]):
            return Response({"error": 1, "detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            existing_obj = Project3DFloorPlanHdr.objects.get(key=pk)
        except Project3DFloorPlanHdr.DoesNotExist:
            return Response({"error": 1, "detail": "Floor plan header not found"}, status=status.HTTP_404_NOT_FOUND)

        file_url = existing_obj.image_url

        if files:
            result = UF.delete_file_from_s3(existing_obj.image_url)

            if not result['success']:
                return Response({"error": 1, "detail": "Error while deleting existing image"}, status=status.HTTP_400_BAD_REQUEST)

            folder_path = UF.create_s3_folder_structure(
                client_id, company_id, project_id, block_id, floor_ids)

            for file in files:
                try:
                    header, base64_data = file.split(',', 1)
                    decoded_file = base64.b64decode(base64_data)
                    file_like = io.BytesIO(decoded_file)

                    file_name = f"{uuid.uuid4()}.jpg"
                    s3_path = f"{folder_path}/{'3D' if image_type == '3D' else 'floor_plan'}/{file_name}"

                    uploaded_url = UF.upload_file_to_s3(s3_path, file_like)
                    if not uploaded_url:
                        return Response({"error": 1, "detail": "Failed to upload project 3d floor plan"}, status=status.HTTP_400_BAD_REQUEST)
                    file_url = uploaded_url
                except Exception as e:
                    return Response({"error": 1, "detail": f"Invalid base64 image format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        existing_obj.image_type = image_type
        existing_obj.image_name = image_name
        existing_obj.image_url = file_url
        existing_obj.client_id_id = client_id
        existing_obj.company_id_id = company_id
        existing_obj.project_id_id = project_id
        existing_obj.block_id_id = block_id
        existing_obj.save()

        Project3DFloorPlanDtl.objects.filter(hdr_key=existing_obj).delete()

        for floor_id in floor_ids:
            dtl_data = {
                "hdr_key": existing_obj.key,
                "floor_id": floor_id
            }
            dtl_serializer = Project3DFloorPlanDtlSerializer(data=dtl_data)
            if dtl_serializer.is_valid():
                dtl_serializer.save()
            else:
                return Response({"error": 0, "detail": f"Error While Adding Image to Floor: {dtl_serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

        final_serializer = Project3DFloorPlanHdrSerializer(existing_obj)
        return Response({"error": 0, "detail": "Project 3D Floor Plan Updated Successfully", "data": final_serializer.data}, status=status.HTTP_200_OK)


class ProjectAllViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = Project.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = ProjectSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        closedStatusList = Projectstatus.objects.filter(
            is_active=False, client_id=clientID, company=companyID).values_list('key', flat=True)

        if len(closedStatusList) > 0:
            serialisedData = ProjectSerializer(
                self.queryset.filter(client_id=clientID, company=companyID).filter(
                    ~Q(projstatus_key__in=closedStatusList)),
                many=True,
                read_only=True,
                fields=('key', 'id', 'name')
            ).data
        else:  # if the closed status not there in project status table
            serialisedData = ProjectSerializer(
                self.queryset.filter(
                    client_id=clientID,
                    company=companyID
                ).order_by('name'),many=True,
                read_only=True,
                fields=('key', 'id', 'name')
            ).data

        return Response(serialisedData)


class AmenityViewset(viewsets.ViewSet):
    queryset = Amenity.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = AmenitySerializer(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        amentyIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = AmenitySerializer(amentyIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        amentyInstance = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = AmenitySerializer(
            amentyInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Amenity Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Amenity PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Amenity PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        request.data['id'] = Amenity().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = AmenitySerializer(data=reqData)
        if serializer.is_valid():
            try:
                amentyIns = serializer.save()
                if amentyIns:
                    return Response({"error": 0, "detail": "Amenity Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Amenity"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectAmenityViewset(viewsets.ViewSet):
    queryset = Projectamenity.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = ProjectAmenitySerializer(
            self.queryset.filter(
                company=companyID,
                client_id=clientID
            ), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectAmentyIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectAmenitySerializer(projectAmentyIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proAmentyInstance = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectAmenitySerializer(
            proAmentyInstance, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Amenity Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Amenity PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Amenity PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectAmenitySerializer(data=reqData)
        if serializer.is_valid():
            try:
                projectAmentyIns = serializer.save()
                if projectAmentyIns:
                    return Response({"error": 0, "detail": "Project Amenity Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Amenity"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjCostCodeViewset(viewsets.ViewSet):
    queryset = Projcostcode.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = ProjCostCodeSerializer(
            self.queryset.filter(
                company=companyID,
                client_id=clientID
            ), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projCostCodeIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjCostCodeSerializer(projCostCodeIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projCostCodeIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjCostCodeSerializer(
            projCostCodeIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Cost Code Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Cost Code PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Cost Code PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjCostCodeSerializer(data=reqData)
        if serializer.is_valid():
            try:
                projCostCodeIns = serializer.save()
                if projCostCodeIns:
                    return Response({"error": 0, "detail": "Project Cost Code Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Cost Code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectBlockViewset(viewsets.GenericViewSet):
    queryset = Projectblock.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectBlockSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project'):
            qrySet = self.queryset.filter(
                proj_key=request.GET.get('project'),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectBlockSerializer(
                qrySet.order_by('-key'), many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet.order_by('-key'))
            serializer = ProjectBlockSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectBlockIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectBlockSerializer(projectBlockIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectBlockIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        projectBlockIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectBlockIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectBlockSerializer(
            projectBlockIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Block Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Block PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Block PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        request.data['id'] = Projectblock().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectBlockSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Block Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Block"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectFloorGenerationView(APIView):
    def post(self, request):
        blocks_payload = request.data.get('blocks', [])
        overwrite = request.query_params.get('overwrite') == '1'

        if not blocks_payload:
            return Response({"error": 1, "detail": "No blocks provided"}, status=status.HTTP_400_BAD_REQUEST)

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        created_floors = []
        blocks_with_existing_floors = []

        floor_names_above = [
            "First Floor", "Second Floor", "Third Floor", "Fourth Floor",
            "Fifth Floor", "Sixth Floor", "Seventh Floor", "Eighth Floor",
            "Ninth Floor", "Tenth Floor"
        ]

        try:
            with transaction.atomic():
                for block in blocks_payload:
                    block_key = block.get('key')

                    project_block = Projectblock.objects.filter(
                        key=block_key,
                        client_id=clientID,
                        company=companyID
                    ).first()
                    if not project_block:
                        continue

                    existing_floors = Projectfloor.objects.filter(projblk_key=project_block)
                    if existing_floors.exists() and not overwrite:
                        blocks_with_existing_floors.append(project_block.descr)

                if blocks_with_existing_floors and not overwrite:
                    return Response(
                        {
                            "error": 2,
                            "detail": "Some blocks already have floors",
                            "blocks": blocks_with_existing_floors
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                for block in blocks_payload:
                    block_key = block.get('key')

                    project_block = Projectblock.objects.filter(
                        key=block_key,
                        client_id=clientID,
                        company=companyID
                    ).first()
                    if not project_block:
                        continue

                    if overwrite:
                        Projectfloor.objects.filter(projblk_key=project_block).delete()

                    created_floors_for_block = []

                    floors_below = project_block.floor_count_blw_ground or 0
                    floors_above = project_block.floor_count_abv_ground or 0

                    for b in range(floors_below, 0, -1):
                        floor_name = f"Basement {b}"
                        floor_obj = Projectfloor.objects.create(
                            projblk_key=project_block,
                            id=Projectfloor.nextID(),
                            descr=floor_name,
                            createdby=UF.getCurrentSessionUser(request),
                            createddttm=timezone.now(),
                            company=project_block.company,
                            client_id=project_block.client_id
                        )
                        created_floors_for_block.append(floor_obj.descr)

                    ground_floor_obj = Projectfloor.objects.create(
                        projblk_key=project_block,
                        id=Projectfloor.nextID(),
                        descr="Ground Floor",
                        createdby=UF.getCurrentSessionUser(request),
                        createddttm=timezone.now(),
                        company=project_block.company,
                        client_id=project_block.client_id
                    )
                    created_floors_for_block.append(ground_floor_obj.descr)

                    for f in range(1, floors_above + 1):
                        floor_name = (
                            floor_names_above[f - 1]
                            if f <= len(floor_names_above)
                            else f"Floor {f}"
                        )
                        floor_obj = Projectfloor.objects.create(
                            projblk_key=project_block,
                            id=Projectfloor.nextID(),
                            descr=floor_name,
                            createdby=UF.getCurrentSessionUser(request),
                            createddttm=timezone.now(),
                            company=project_block.company,
                            client_id=project_block.client_id
                        )
                        created_floors_for_block.append(floor_obj.descr)

                    created_floors.extend(created_floors_for_block)

            return Response(
                {
                    "error": 0,
                    "detail": "Floors created successfully",
                    "created_floors": created_floors
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProjectFloorViewset(viewsets.GenericViewSet):
    queryset = Projectfloor.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectFloorSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            company=companyID,
            client_id=clientID
        )

        if request.GET.get('project'):
            qrySet = self.queryset.filter(
                projblk_key__proj_key=request.GET.get('project'),
            )

        if request.GET.get('project_block'):
            qrySet = self.queryset.filter(
                projblk_key=request.GET.get('project_block'),
            )

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectFloorSerializer(
                qrySet.order_by('-key'), many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet.order_by('-key'))
            serializer = ProjectFloorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectFloorIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectFloorSerializer(projectFloorIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectFloorIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        projectFloorIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectFloorIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectFloorSerializer(
            projectFloorIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Floor Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Floor PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Floor PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data

        try:
            block_obj = Projectblock.objects.get(key=reqData.get('projblk_key'))
        except Projectblock.DoesNotExist:
            return Response({"error": 1, "detail": "Invalid Project Block Key"}, status=status.HTTP_400_BAD_REQUEST)

        floor_count_allowed = (
            (block_obj.floor_count_abv_ground or 0)
            + (block_obj.floor_count_blw_ground or 0)
            + 1
        )

        existing_floor_count = Projectfloor.objects.filter(projblk_key=reqData.get('projblk_key')).count()

        if existing_floor_count >= floor_count_allowed:
            return Response(
                {
                    "error": 1,
                    "detail": f"Cannot create more floors than defined in Project Block (Limit: {floor_count_allowed})"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data['id'] = Projectfloor().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectFloorSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Floor Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Floor"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectUnitGenerationView(APIView):

    def post(self, request):
        floors_payload = request.data.get('floors', [])
        overwrite = request.query_params.get('overwrite') == '1'

        if not floors_payload:
            return Response(
                {"error": 1, "detail": "No floors provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        created_units = []
        floors_with_existing_units = {}

        floor_prefix_map = {
            "First Floor": "1",
            "Second Floor": "2",
            "Third Floor": "3",
            "Fourth Floor": "4",
            "Fifth Floor": "5",
            "Sixth Floor": "6",
            "Seventh Floor": "7",
            "Eighth Floor": "8",
            "Ninth Floor": "9",
            "Tenth Floor": "10",
        }

        def _to_letters(n):
            letters = ""
            while n > 0:
                n, rem = divmod(n - 1, 26)
                letters = chr(65 + rem) + letters
            return letters

        def _get_unit_prefix(floor_name):
            name = (floor_name or "").strip()
            if not name:
                return "U"
            if name == "Ground Floor":
                return "G"
            if name in floor_prefix_map:
                return floor_prefix_map[name]
            # Basement handling: "Basement 1", "Basement 2", etc.
            if name.lower().startswith("basement"):
                parts = name.split()
                if len(parts) > 1 and parts[-1].isdigit():
                    return f"B{parts[-1]}"
                return "B"
            # Numeric floors: "11th Floor", "12 Floor", etc.
            num = "".join(ch for ch in name if ch.isdigit())
            if num:
                return num
            return "U"

        try:
            with transaction.atomic():
                for floor_item in floors_payload:
                    floor_key = floor_item.get('key')
                    floor_obj = Projectfloor.objects.filter(
                        key=floor_key,
                        projblk_key__client_id=clientID,
                        projblk_key__company=companyID
                    ).first()
                    if floor_obj:
                        existing_units = Projectunit.objects.filter(projflr_key=floor_obj)
                        if existing_units.exists():
                            block_name = floor_obj.projblk_key.descr
                            if block_name not in floors_with_existing_units:
                                floors_with_existing_units[block_name] = []
                            floors_with_existing_units[block_name].append(floor_obj.descr)

                if floors_with_existing_units and not overwrite:
                    return Response({
                        "error": 2,
                        "detail": "Some floors already have units",
                        "floors": floors_with_existing_units
                    }, status=status.HTTP_400_BAD_REQUEST)

                for floor_item in floors_payload:
                    floor_key = floor_item.get('key')
                    unit_count = floor_item.get('unit_count', 0)

                    floor_obj = Projectfloor.objects.filter(
                        key=floor_key,
                        projblk_key__client_id=clientID,
                        projblk_key__company=companyID
                    ).first()
                    if not floor_obj:
                        continue

                    if overwrite:
                        Projectunit.objects.filter(projflr_key=floor_obj).delete()

                    # Get prefix from the mapping or basement naming
                    prefix = _get_unit_prefix(floor_obj.descr)

                    for i in range(1, unit_count + 1):
                        suffix = _to_letters(i)
                        if prefix == "G":
                            unit_descr = f"G{suffix}"
                        else:
                            unit_descr = f"{prefix}{suffix}"
                        unit_obj = Projectunit.objects.create(
                            projflr_key=floor_obj,
                            projblk_key=floor_obj.projblk_key,
                            proj_key=floor_obj.projblk_key.proj_key,
                            id=Projectunit.nextID(),
                            descr=unit_descr,
                            createdby=UF.getCurrentSessionUser(request),
                            createddttm=timezone.now(),
                            company=floor_obj.projblk_key.company,
                            client_id=floor_obj.projblk_key.client_id
                        )
                        created_units.append(unit_obj.id)

            return Response({
                "error": 0,
                "detail": "Units created successfully",
                "created_unit_ids": created_units,
                "floors": [f.get('key') for f in floors_payload]
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProjectUnitStatusViewset(viewsets.ViewSet):
    queryset = ProjectUnitStatus.objects.all()
    # permission_classes = [AllowAny, ]

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        serializer_class = ProjectUnitStatusSerializer(
            self.queryset.filter(
                company=companyID,
                client_id=clientID
            ), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = ProjectUnitStatusSerializer(statusIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company=companyID,
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
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer = ProjectUnitStatusSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project unit status Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project unit status PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project unit status PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):

        serializer = ProjectUnitStatusSerializer(data=request.data)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Project Unit Status Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": f"Error While Adding Project Unit Status: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": f"Error in API request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)


class ProjectUnitViewset(viewsets.GenericViewSet):
    queryset = Projectunit.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectUnitSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
                        company=companyID,
                        client_id=clientID
                    ).order_by('key')
        
        if request.GET.get('project'):
            qrySet = self.queryset.filter(
                proj_key=request.GET.get('project'),
                company=companyID,
                client_id=clientID
            )
        if request.GET.get('project_block'):
            qrySet = self.queryset.filter(
                projblk_key=request.GET.get('project_block'),
                company=companyID,
                client_id=clientID
            )
        if request.GET.get('project_floor'):
            qrySet = self.queryset.filter(
                projflr_key=request.GET.get('project_floor'),
                company=companyID,
                client_id=clientID
            )

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectUnitSerializer(
                qrySet.order_by('key'), many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet.order_by('key'))
            serializer = ProjectUnitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proUnitIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = ProjectUnitSerializer(proUnitIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectUnitIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        projectUnitIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectUnitIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectUnitSerializer(
            projectUnitIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Unit Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Unit PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Unit PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data

        try:
            floor_obj = Projectfloor.objects.get(key=reqData.get('projflr_key'))
        except Projectfloor.DoesNotExist:
            return Response(
                {"error": 1, "detail": "Invalid Project Floor Key"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            allowed_units = int(floor_obj.no_of_units or 0)
        except (TypeError, ValueError):
            allowed_units = 0

        existing_unit_count = Projectunit.objects.filter(
            projflr_key=reqData.get('projflr_key')
        ).count()

        if allowed_units > 0 and existing_unit_count >= allowed_units:
            return Response(
                {"error": 1, "detail": "Cannot create more units than defined in Project Floor"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data['id'] = Projectunit().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        reqData['unitstatus'] = 'A'  # available while create
        serializer = ProjectUnitSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Unit Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Floor"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectAvailableUnitViewset(viewsets.GenericViewSet):
    queryset = Projectunit.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ProjectUnitSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        project = request.GET.get('project')
        block = request.GET.get('block')

        if project and block:
            qrySet = self.queryset.filter(
                proj_key=project,
                projblk_key=block,
                projunit_status_key__descr="Available",
                company=companyID,
                client_id=clientID
            )

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectUnitSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = ProjectUnitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class ProjectAvailabilityCategoryViewset(viewsets.GenericViewSet):
    queryset = Projectunit.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage

    def list(self, request, pk=None):
        UF = UtilFunctions()

        statusList = [UF.getFullUnitStatus(status_code) for status_code in Projectunit.objects.filter(
            unitstatus__isnull=False).values_list('unitstatus', flat=True).distinct()]
        statusList.append({
            "label": "All",
            "value": "",
        })
        sortedStatusList = sorted(statusList, key=lambda d: d['label'])

        return Response({
            "error": 0,
            "detail": "Success",
            "data": sortedStatusList
        }, status=status.HTTP_400_BAD_REQUEST)


class ProjectAvailabilityViewset(viewsets.GenericViewSet):
    queryset = Project.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        blockIns = Projectblock.objects.filter(
            proj_key=pk,
            company=companyID,
            client_id=clientID
        )

        if blockIns.count() > 0:
            returnData = []

            projectBlocks = ProjectBlockSerializer(
                blockIns, many=True, fields=('key', 'id', 'descr',)).data

            for block in projectBlocks:  # to obtain floors
                floorIns = Projectfloor.objects.filter(
                    projblk_key=block['key'])
                projectFloors = ProjectFloorSerializer(
                    floorIns, many=True, fields=('key', 'id', 'descr')).data

                for floor in projectFloors:  # to obtain units

                    if request.GET.get('status'):
                        statusFilter = request.GET.get('status').upper()
                        if statusFilter == "A":
                            unitIns = Projectunit.objects.filter(
                                projflr_key=floor['key'], projblk_key=block['key']).filter(
                                Q(unitstatus=statusFilter) | Q(unitstatus__isnull=True))
                        else:
                            unitIns = Projectunit.objects.filter(
                                projflr_key=floor['key'], projblk_key=block['key'], unitstatus=statusFilter)
                    else:
                        unitIns = Projectunit.objects.filter(
                            projflr_key=floor['key'], projblk_key=block['key'])

                    projectUnits = ProjectUnitSerializer(
                        unitIns, many=True,
                        fields=('key', 'id', 'descr', 'unitstatus', 'saleablearea', 'udsarea', 'carpetarea')).data

                    for unit in projectUnits:  # to prepare result set
                        returnData.append({
                            "block": block["id"],
                            "description": block["descr"],
                            "floor": floor["id"],
                            "Unit": unit["id"],
                            "status": unit["unitstatus"],
                            "sale_area": unit["saleablearea"],
                            "usd_area": unit["udsarea"],
                            "carpet_area": unit["carpetarea"],
                        })

            page_nmbr = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', settings.DATA_PER_PAGE)

            uf = UtilFunctions()

            return Response({
                "error": 0,
                "detail": "Data returned successfully",
                ** uf.getPaginatedResultList(returnData, page_nmbr, page_size)
            }, status=status.HTTP_200_OK)

        return Response({"error": 1, "detail": "This project is does not have any blocks available right now.", "data": []}, status=status.HTTP_400_BAD_REQUEST)


class ProjectPayTermViewset(viewsets.GenericViewSet):
    queryset = Projpayterms.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjPayTermsSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project'):
            qrySet = self.queryset.filter(
                proj_key=request.GET.get('project'),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        page = self.paginate_queryset(qrySet.order_by('-key'))
        serializer = ProjPayTermsSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectPayTermIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        serializer_class = ProjPayTermsSerializer(projectPayTermIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectPayTermIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)
        projectPayTermIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectPayTermIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjPayTermsSerializer(
            projectPayTermIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Pay Term Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Pay Term PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Pay Term PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjPayTermsSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Pay Term Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Pay Term"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectPriceHistoryViewset(viewsets.GenericViewSet):
    queryset = Projpricehistory.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjPriceHistorySerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project'):
            qrySet = self.queryset.filter(
                proj_key=request.GET.get('project'),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        page = self.paginate_queryset(qrySet.order_by('-key'))
        serializer = ProjPriceHistorySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectPriceHistoryIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjPriceHistorySerializer(projectPriceHistoryIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectPriceHistoryIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        projectPriceHistoryIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectPriceHistoryIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjPriceHistorySerializer(
            projectPriceHistoryIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Price History Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Price History PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Price History PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjPriceHistorySerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Price History Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Price History"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjStatusHistoryViewset(viewsets.GenericViewSet):
    queryset = Projstatushistory.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjStatusHistorySerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project'):
            qrySet = self.queryset.filter(
                proj_key=request.GET.get('project'),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        page = self.paginate_queryset(qrySet.order_by('-createddttm'))
        serializer = ProjStatusHistorySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectStatusHistoryIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjStatusHistorySerializer(projectStatusHistoryIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectStatusHistoryIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        projectStatusHistoryIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectStatusHistoryIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjStatusHistorySerializer(
            projectStatusHistoryIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Status History Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Status History PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Status History PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjStatusHistorySerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Status History Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Status History"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectWorkViewset(viewsets.GenericViewSet):
    queryset = ProjectWork.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectWorkSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        project = request.GET.get('project', False)
        block = request.GET.get('block', False)
        category = request.GET.get('category', False)
        type = request.GET.get('type', False)

        if project and block and category and type:
            qrySet = self.queryset.filter(
                project_key=project,
                block_key=block,
                category_key=category,
                type_key=type,
                company_id=companyID,
                client_id=clientID
            )

        else:
            qrySet = self.queryset.filter(
                company_id=companyID,
                client_id=clientID
            )
        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectWorkSerializer(
                qrySet, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet.order_by('-key'))
            serializer = ProjectWorkSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proWorkIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectWorkSerializer(proWorkIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proWorkIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        proWorkIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proWorkIns = get_object_or_404(self.queryset.filter(
            company_id=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectWorkSerializer(
            proWorkIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Work Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Work PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Work PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        reqData['created_by'] = UF.getCurrentSessionUser(request)
        reqData['company_id'] = companyID
        reqData['client_id'] = clientID
        serializer = ProjectWorkSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Work Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Work"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectStageViewset(viewsets.GenericViewSet):
    queryset = Projectstage.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectStageSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project', False):
            qrySet = self.queryset.filter(
                projwrk_key__in=ProjectWork.objects.filter(
                    proj_key=request.GET.get('project'),
                    company_id=companyID,
                    client_id=clientID
                ).values_list('key', flat=True)
            )
        elif request.GET.get('work_key', False):
            qrySet = self.queryset.filter(
                projwrk_key=request.GET.get('work_key'),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectStageSerializer(
                qrySet, many=True, fields=('key', 'id', 'descr'))
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(qrySet.order_by('-key'))
            serializer = ProjectStageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectStageIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectStageSerializer(projectStageIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectStageIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        projectStageIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        projectStageIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectStageSerializer(
            projectStageIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Stage Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Stage PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Stage PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        request.data['id'] = Projectstage().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectStageSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Stage Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Stage"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectBulkTaskViewset(viewsets.GenericViewSet):
    queryset = Projecttask.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectTaskSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project', False):
            qrySet = self.queryset.filter(
                projstg_key__in=Projectstage.objects.filter(
                    projwrk_key__in=ProjectWork.objects.filter(
                        proj_key=request.GET.get('project'),
                        company_id=companyID,
                        client_id=clientID
                    ).values_list('key', flat=True),
                    company=companyID,
                    client_id=clientID
                ).values_list('key', flat=True),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        page = self.paginate_queryset(qrySet.order_by('-key'))
        serializer = ProjectTaskSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTaskIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectTaskSerializer(proTaskIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTaskIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        proTaskIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTaskIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectTaskSerializer(
            proTaskIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Task Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Task PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Task PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def rollBack(self, workKeys, stageKeys, taskKeys):
        if len(stageKeys) > 0:
            Projectstage.objects.filter(
                key__in=stageKeys
            ).delete()
        if len(workKeys) > 0:
            ProjectWork.objects.filter(
                key__in=workKeys
            ).delete()
        if len(workKeys) > 0:
            Projecttask.objects.filter(
                key__in=taskKeys
            ).delete()

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        successfullyInsertedWorksKeys = []
        successfullyInsertedStageKeys = []
        successfullyInsertedTasksKeys = []
        oveallTaskData = []

        #

        # FOR WORK
        for wrk in reqData['works']:
            wrk['company_id'] = reqData['company_id']
            wrk['client_id'] = reqData['client_id']
            wrk['proj_key'] = reqData['proj_key']
            wrk['createdby'] = reqData['createdby']
            workSer = ProjectWorkSerializer(data=wrk)
            try:
                if workSer.is_valid():
                    workSer.save()
                    workKey = workSer.data['key']
                    successfullyInsertedWorksKeys.append(workKey)

                    # FOR STAGE
                    for stg in wrk['stages']:
                        stg['projwrk_key'] = workKey
                        stg['id'] = Projectstage().nextId()
                        stg['company'] = reqData['company_id']
                        stg['client_id'] = reqData['client_id']
                        stg['createdby'] = reqData['createdby']
                        stageSer = ProjectStageSerializer(data=stg)
                        if stageSer.is_valid():
                            stageSer.save()
                            stgKey = stageSer.data['key']
                            successfullyInsertedStageKeys.append(stgKey)

                            # FOR TASK
                            for tsk in stg['tasks']:
                                tsk['projstg_key'] = stgKey
                                tsk['id'] = Projecttask().nextId()
                                tsk['company'] = reqData['company_id']
                                tsk['client_id'] = reqData['client_id']
                                tsk['createdby'] = reqData['createdby']
                                tskSer = ProjectTaskSerializer(data=tsk)
                                if tskSer.is_valid():
                                    tskSer.save()
                                    tskKey = tskSer.data['key']
                                    successfullyInsertedTasksKeys.append(
                                        tskKey)
                                    oveallTaskData.append(tskSer.data)
                                else:
                                    # ROLE BACK
                                    self.rollBack(
                                        successfullyInsertedWorksKeys,
                                        successfullyInsertedStageKeys,
                                        successfullyInsertedTasksKeys
                                    )
                                    return Response({"error": 1, "detail": "Error In Task Items data", "data": tskSer.errors}, status=status.HTTP_400_BAD_REQUEST)

                        else:
                            # ROLE BACK
                            self.rollBack(
                                successfullyInsertedWorksKeys,
                                successfullyInsertedStageKeys,
                                successfullyInsertedTasksKeys
                            )
                            return Response({"error": 1, "detail": "Error In Stage Items data", "data": stageSer.errors}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    # ROLE BACK
                    self.rollBack(
                        successfullyInsertedWorksKeys,
                        successfullyInsertedStageKeys,
                        successfullyInsertedTasksKeys
                    )
                    return Response({"error": 1, "detail": "Error In Work Items data", "data": workSer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except:
                # ROLE BACK
                self.rollBack(
                    successfullyInsertedWorksKeys,
                    successfullyInsertedStageKeys,
                    successfullyInsertedTasksKeys
                )
                return Response({"error": 1, "detail": "Something went wrong", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": 0, "detail": "Work, Stage and Task details added successfully", "data": oveallTaskData}, status=status.HTTP_200_OK)


class ProjectBulkEditTaskViewset(viewsets.GenericViewSet):
    queryset = Projecttask.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectTaskSerializer

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)

        projectKey = reqData['proj_key']

        exstWorkId = ProjectWork.objects.filter(
            proj_key=projectKey
        ).values_list('key', flat=True)

        exstStageId = Projectstage.objects.filter(
            projwrk_key__in=exstWorkId
        ).values_list('key', flat=True)

        exstTaskId = Projecttask.objects.filter(
            projstg_key__in=exstStageId
        ).values_list('key', flat=True)

        successfullyInsertedWorksKeys = []
        successfullyInsertedStageKeys = []
        successfullyInsertedTasksKeys = []
        oveallTaskData = []

        # #

        # FOR WORK
        for wrk in reqData['works']:

            if wrk.get("key", False) and not wrk.get("key") == "null":
                # existing work
                wrk.pop('createddttm')
                wrk.pop('createdby')
                wrk.pop('company_id')
                wrk.pop('client_id')
                wrk.pop('proj_key')
                wrk['lastmodifiedby'] = reqData['createdby']
                wrk['lastmodifieddttm'] = UF.getCurrentDateAndTime()
                workSer = ProjectWorkSerializer(
                    ProjectWork.objects.get(
                        key=wrk.get("key")
                    ),
                    data=wrk,
                    partial=True
                )
            else:
                wrk['company_id'] = reqData['company_id']
                wrk['client_id'] = reqData['client_id']
                wrk['proj_key'] = reqData['proj_key']
                wrk['createdby'] = reqData['createdby']
                workSer = ProjectWorkSerializer(data=wrk)

            try:
                if workSer.is_valid():
                    workSer.save()
                    workKey = workSer.data['key']
                    successfullyInsertedWorksKeys.append(workKey)

                    # FOR STAGE
                    for stg in wrk['stages']:
                        if stg.get("key", False) and not stg.get("key") == "null":
                            # existing work
                            stg.pop('createddttm')
                            stg.pop('createdby')
                            stg.pop('company')
                            stg.pop('client_id')
                            stg.pop('projwrk_key')
                            stg['lastmodifiedby'] = reqData['createdby']
                            stg['lastmodifieddttm'] = UF.getCurrentDateAndTime()
                            stageSer = ProjectStageSerializer(
                                Projectstage.objects.get(
                                    key=stg.get("key")
                                ),
                                data=stg,
                                partial=True
                            )
                        else:
                            stg['id'] = Projectstage().nextID()
                            stg['projwrk_key'] = workKey
                            stg['company'] = reqData['company_id']
                            stg['client_id'] = reqData['client_id']
                            stg['createdby'] = reqData['createdby']
                            stageSer = ProjectStageSerializer(data=stg)

                        try:
                            if stageSer.is_valid():
                                stageSer.save()
                                stgKey = stageSer.data['key']
                                successfullyInsertedStageKeys.append(stgKey)

                                # FOR TASK
                                for tsk in stg['tasks']:

                                    if tsk.get("key", False) and not tsk.get("key") == "null":
                                        # existing work
                                        tsk.pop('createddttm')
                                        tsk.pop('createdby')
                                        tsk.pop('company')
                                        tsk.pop('client_id')
                                        tsk.pop('projstg_key')
                                        tsk['lastmodifiedby'] = reqData['createdby']
                                        tsk['lastmodifieddttm'] = UF.getCurrentDateAndTime()
                                        tskSer = ProjectTaskSerializer(
                                            Projecttask.objects.get(
                                                key=tsk.get("key")
                                            ),
                                            data=tsk,
                                            partial=True
                                        )
                                    else:
                                        tsk['id'] = Projecttask().nextID()
                                        tsk['projstg_key'] = stgKey
                                        tsk['company'] = reqData['company_id']
                                        tsk['client_id'] = reqData['client_id']
                                        tsk['createdby'] = reqData['createdby']
                                        tskSer = ProjectTaskSerializer(
                                            data=tsk)

                                    try:
                                        if tskSer.is_valid():
                                            tskSer.save()
                                            tskKey = tskSer.data['key']
                                            successfullyInsertedTasksKeys.append(
                                                tskKey)
                                            oveallTaskData.append(tskSer.data)
                                        else:
                                            return Response({"error": 1, "detail": "Error In Task Items data", "data": tskSer.errors}, status=status.HTTP_400_BAD_REQUEST)
                                    except:
                                        return Response({"error": 1, "detail": "Something went wrong in TASK update", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

                            else:
                                return Response({"error": 1, "detail": "Error In Stage Items data", "data": stageSer.errors}, status=status.HTTP_400_BAD_REQUEST)
                        except:
                            return Response({"error": 1, "detail": "Something went wrong in Stage Update", "data": {}}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": 1, "detail": "Error In Work Items data", "data": workSer.errors}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": 1, "detail": "Something went wrong in Work Update", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        worksToBeRemoved = [
            i for i in exstWorkId if i not in successfullyInsertedWorksKeys]
        stageTOBeRemoved = [
            i for i in exstStageId if i not in successfullyInsertedStageKeys]
        taskTOBeRemoved = [
            i for i in exstTaskId if i not in successfullyInsertedTasksKeys]

        Projecttask.objects.filter(
            key__in=taskTOBeRemoved
        ).delete()

        Projectstage.objects.filter(
            key__in=stageTOBeRemoved
        ).delete()

        ProjectWork.objects.filter(
            key__in=worksToBeRemoved
        ).delete()

        return Response({
            "error": 0,
            "detail": "Work, Stage and Task details modified successfully",
            "data": oveallTaskData,
            "removed_items": {
                "work": worksToBeRemoved,
                "stage": stageTOBeRemoved,
                "task": taskTOBeRemoved
            }},
            status=status.HTTP_200_OK)


class ProjectTaskReverseViewset(viewsets.GenericViewSet):
    queryset = Projecttask.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectTaskSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        if request.GET.get('project', False):

            works = ProjectWorkSerializer(
                ProjectWork.objects.filter(
                    proj_key=request.GET.get('project'),
                    company_id=companyID,
                    client_id=clientID
                ),
                many=True
            ).data

            final = []

            # looping works
            for wrk in works:

                stages = ProjectStageSerializer(
                    Projectstage.objects.filter(
                        projwrk_key=wrk.get('key'),
                        company=companyID,
                        client_id=clientID
                    ),
                    many=True
                ).data

                # looping stages
                for stg in stages:
                    tasks = ProjectTaskSerializer(
                        Projecttask.objects.filter(
                            projstg_key=stg.get('key'),
                            company=companyID,
                            client_id=clientID
                        ),
                        many=True
                    ).data
                    stg['tasks'] = tasks

                wrk['stages'] = stages
                final.append(wrk)

            return Response(final)
        else:
            return Response({"error": 1, "detail": "Project ID query param missing"}, status=status.HTTP_400_BAD_REQUEST)


class ProjectTaskViewset(viewsets.GenericViewSet):
    queryset = Projecttask.objects.all()
    # permission_classes = [AllowAny, ]
    pagination_class = Pagination10PerPage
    serializer_class = ProjectTaskSerializer

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ))

        if request.GET.get('project', False):
            qrySet = self.queryset.filter(
                projstg_key__in=Projectstage.objects.filter(
                    projwrk_key__in=ProjectWork.objects.filter(
                        proj_key=request.GET.get('project'),
                        company_id=companyID,
                        client_id=clientID
                    ).values_list('key', flat=True),
                    company=companyID,
                    client_id=clientID
                ).values_list('key', flat=True),
                company=companyID,
                client_id=clientID
            )
        elif request.GET.get('stage_key', False):
            qrySet = self.queryset.filter(
                projstg_key=request.GET.get('stage_key'),
                company=companyID,
                client_id=clientID
            )
        else:
            qrySet = self.queryset.filter(
                company=companyID,
                client_id=clientID
            )

        page = self.paginate_queryset(qrySet.order_by('-key'))
        serializer = ProjectTaskSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTaskIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        serializer_class = ProjectTaskSerializer(proTaskIns)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTaskIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        proTaskIns.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        proTaskIns = get_object_or_404(self.queryset.filter(
            company=companyID,
            client_id=clientID
        ), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectTaskSerializer(
            proTaskIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Project Task Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Project Task PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Project Task PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['id'] = Projecttask().nextID()
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectTaskSerializer(data=reqData)
        if serializer.is_valid():
            try:
                project = serializer.save()
                if project:
                    return Response({"error": 0, "detail": "Project Task Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding Project Task"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class NonTaskProjectViewset(viewsets.ViewSet):
    def list(self, request):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        stageKeys = list(
            set(Projecttask.objects.filter(
                company=companyID,
                client_id=clientID
            ).values_list('projstg_key', flat=True)))

        workKeys = list(
            set(Projectstage.objects.filter(
                key__in=stageKeys,
                company=companyID,
                client_id=clientID
            ).values_list('projwrk_key', flat=True)))

        projKeys = list(
            set(ProjectWork.objects.filter(
                key__in=workKeys,
                company_id=companyID,
                client_id=clientID
            ).values_list('proj_key', flat=True)))

        nonTaskProjets = ProjectSerializer(
            Project.objects.filter(
                company=companyID,
                client_id=clientID
            ).filter(
                ~Q(key__in=projKeys)
            ),
            many=True,
            fields=('key', 'id', 'name')
        ).data

        return Response(nonTaskProjets)


class ExpenseVendorViewset(viewsets.GenericViewSet):
    queryset = ExpenseVendor.objects.all()
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ExpenseVendorSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = ExpenseVendorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = ExpenseVendorSerializer(statusIns)
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
        serializer = ExpenseVendorSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Expense Vendor Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Expense Vendor PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Expense Vendor PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        reqData = request.data
        reqData['client_id'] = clientID
        serializer = ExpenseVendorSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Expense Vendor Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Expense Vendor", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ExpenseTypeViewset(viewsets.GenericViewSet):
    queryset = ExpenseType.objects.all()
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ExpenseTypeSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = ExpenseTypeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        statusIns = get_object_or_404(self.queryset.filter(
            client_id=clientID
        ), pk=pk)
        serializer_class = ExpenseTypeSerializer(statusIns)
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
        serializer = ExpenseTypeSerializer(
            statusIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Expense type Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Expense type PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Expense type PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])
        reqData = request.data
        reqData['client_id'] = clientID
        serializer = ExpenseTypeSerializer(data=reqData)
        if serializer.is_valid():

            try:
                statusIns = serializer.save()
                if statusIns:
                    return Response({"error": 0, "detail": "Expense type Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": "Error While Adding Expense type", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PaidExpensesViewset(viewsets.GenericViewSet):
    queryset = PaidExpenses.objects.all()
    serializer_class = PaidExpensesSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID, company_id=companyID).order_by('-date')

        project = request.GET.get("project")
        if project:
            qrySet = qrySet.filter(
                project_key=project, client_id=clientID, company_id=companyID)

        expense_type = request.GET.get("expense_type")
        if project and expense_type:
            qrySet = qrySet.filter(
                project_key=project, expense_type=expense_type,  client_id=clientID, company_id=companyID)

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = PaidExpensesSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:
            page = self.paginate_queryset(qrySet)
            serializer = PaidExpensesSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        expenses_ins = get_object_or_404(self.queryset.filter(
            client_id=clientID, company_id=companyID), pk=pk)
        serializer_class = PaidExpensesSerializer(expenses_ins)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        expenses_ins = get_object_or_404(self.queryset.filter(
            client_id=clientID, company_id=companyID), pk=pk)
        expenses_ins.delete()
        return Response("Delete Success")

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        expenses_ins = get_object_or_404(self.queryset.filter(
            client_id=clientID, company_id=companyID), pk=pk)
        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = PaidExpensesSerializer(
            expenses_ins, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Paid Expense Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In Paid Expense PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In Paid Expense PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        request.data.update({
            'client_id': clientID,
            'company_id': companyID,
            'createdby': UF.getCurrentSessionUser(request)
        })

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "Paid Expense Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": 1, "detail": f"Error While Adding Paid Expense: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectScheduleViewset(viewsets.GenericViewSet):
    queryset = ProjectSchedule.objects.all()
    # permission_classes = [AllowAny, ]
    serializer_class = ProjectScheduleSerializer
    pagination_class = Pagination10PerPage

    def list(self, request):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        qrySet = self.queryset.filter(
            client_id=clientID).order_by('-key')

        if request.GET.get("proj_type", False):
            qset = self.queryset.filter(
                client_id=clientID,
                projtype_key=request.GET.get("proj_type")
            ).order_by('-key')
            serializer = ProjectScheduleSerializer(qset, many=True)
            return Response(serializer.data)

        if (request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1):
            serializer = ProjectScheduleSerializer(
                qrySet, many=True)
            return Response(serializer.data)

        else:

            if request.GET.get("type", False):
                qrySet = qrySet.filter(itemtyp_key=request.GET.get("type"))

            page = self.paginate_queryset(qrySet)
            serializer = ProjectScheduleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ProjectScheduleIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)
        serializer_class = ProjectScheduleSerializer(ProjectScheduleIns)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ProjectScheduleIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        reqData = request.data
        reqData['lastmodifiedby'] = UF.getCurrentSessionUser(request)
        reqData['lastmodifieddttm'] = datetime.today().strftime(
            '%Y-%m-%d %H:%M:%S')

        serializer = ProjectScheduleSerializer(
            ProjectScheduleIns, data=reqData, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"error": 0, "detail": "ProjectSchedule Updated Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error In ProjectSchedule PUT Request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": "Error In ProjectSchedule PUT Request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        ProjectScheduleIns = get_object_or_404(self.queryset.filter(
            client_id=clientID), pk=pk)

        ProjectScheduleIns.delete()
        return Response("Delete Success")

    def create(self, request):
        UF = UtilFunctions()
        reqData = request.data
        reqData['createdby'] = UF.getCurrentSessionUser(request)
        serializer = ProjectScheduleSerializer(data=reqData)
        if serializer.is_valid():
            try:
                ProjectScheduleIns = serializer.save()
                if ProjectScheduleIns:
                    return Response({"error": 0, "detail": "ProjectSchedule Added Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": 1, "detail": "Error While Adding ProjectSchedule"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": 1, "detail": "Error in API request", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
