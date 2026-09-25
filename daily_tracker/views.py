from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from buildiq.utils import UtilFunctions
from .models import DailyWorkProgressHdr, DailyWorkProgressDtl, DailyWorkProgressImage
from .serializers import (
    DailyWorkProgressHdrSerializer, DailyWorkProgressDtlSerializer, DailyWorkProgressImageSerializer
)
from buildiq.pagenation_configs import Pagination10PerPage
import io
import base64
import uuid
from django.utils import timezone

class DailyWorkProgressViewSet(viewsets.ModelViewSet):
    queryset = DailyWorkProgressHdr.objects.all()
    serializer_class = DailyWorkProgressHdrSerializer
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

        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if from_date and to_date:
            if from_date <= to_date:
                try:
                    qrySet = qrySet.filter(
                        date__gte=from_date, date__lte=to_date)
                except ValueError:
                    return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Invalid date values. From date has to be lower than To date"}, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('project', False):
            qrySet = qrySet.filter(
                project_key=request.GET.get('project'),
            )

        if request.GET.get('type', False):
            qrySet = qrySet.filter(
                workctgry_key=request.GET.get('type'),
            )

        list_fields = ['key', 'project_name',
                       'work_ctgry_name', 'status_label', 'date']

        if request.GET.get("without_pagination", False) and int(request.GET.get("without_pagination")) == 1:
            serializer = DailyWorkProgressHdrSerializer(
                qrySet, many=True, fields=list_fields)
            return Response(serializer.data)

        page = self.paginate_queryset(qrySet)
        if page is not None:
            serializer = DailyWorkProgressHdrSerializer(
                page, many=True, fields=list_fields)
            return self.get_paginated_response(serializer.data)

        serializer = DailyWorkProgressHdrSerializer(
            qrySet, many=True, fields=list_fields)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            obj = self.queryset.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': 1, "detail": f"DailyWorkProgress with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DailyWorkProgressHdrSerializer(obj, many=False)
        return Response(serializer.data)

    def delete(self, request, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        try:
            instance = self.queryset.get(
                company_id=companyID,
                client_id=clientID,
                key=pk
            )
            dtl_obj_keys = DailyWorkProgressDtl.objects.filter(hdr_key=instance).values_list('key',flat=True)
            if dtl_obj_keys:
                images_to_delete = DailyWorkProgressImage.objects.filter(dtl_key__in=dtl_obj_keys)
                for image in images_to_delete:
                    try:
                        s3_result = UF.delete_file_from_s3(image.image_url)
                        if not s3_result.get("success"):
                            print(f"Failed to delete S3 file {image.image_url}: {s3_result.get('error')}")

                    except Exception as e:
                        print('Error occured while deleting s3 image: ', str(e))
                        return Response({'error' : 'Error occured while trying to delete images'}, status=status.HTTP_404_NOT_FOUND)
                    
            instance.delete()
            return Response({"detail": "Delete Success"}, status=status.HTTP_200_OK)
        except self.queryset.model.DoesNotExist:
            return Response(
                {'error': f"DailyWorkProgressHdr with id {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Delete Failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            UF = UtilFunctions()

            isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
            if not isValid:
                return Response({'message': returnObj['message']}, status=returnObj['http_status'])

            reqData = request.data
            user = UF.getCurrentSessionUser(request)

            reqData['client_id'] = clientID
            reqData['company_id'] = companyID
            reqData['created_by'] = user

            project_id = reqData.get('project_key')
            block_id = reqData.get('blk_key')
            floor_id = reqData.get('floor_key')
            unit_id = reqData.get('unit_key')

            if not all([clientID, companyID, project_id, block_id, floor_id]):
                return Response({"error": 1, "detail": "Missing required header fields."}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Create Header
            hdr = DailyWorkProgressHdr.objects.create(
                workctgry_key_id=reqData.get('workctgry_key'),
                project_key_id=project_id,
                blk_key_id=block_id,
                floor_key_id=floor_id,
                unit_key_id=unit_id,
                status=reqData.get('status'),
                date=reqData.get('date'),
                created_by=user,
                client_id_id=clientID,
                company_id_id=companyID,
            )

            # 2. S3 folder path
            s3_folder_path = UF.create_s3_folder_structure(
                clientID, companyID, project_id, block_id, [floor_id]
            )
            full_s3_path = f"{s3_folder_path}/daily_progress"

            # 3. Handle Details
            for detail in reqData.get('details', []):
                dtl = DailyWorkProgressDtl.objects.create(
                    hdr_key=hdr,
                    descr=detail.get('descr'),
                    comments=detail.get('comments'),
                    status=detail.get('status'),
                    created_by=user,
                    created_at= detail.get('created_at',timezone.now()),
                    client_id_id=clientID,
                )

                for image in detail.get('images', []):
                    base64_img = image.get('image_url')
                    if not base64_img:
                        continue

                    try:
                        header, base64_data = base64_img.split(',', 1)
                        decoded_file = base64.b64decode(base64_data)
                        file_like = io.BytesIO(decoded_file)

                        file_name = f"{uuid.uuid4()}.jpg"
                        s3_path = f"{full_s3_path}/{file_name}"

                        s3_url = UF.upload_file_to_s3(s3_path, file_like)
                        if not s3_url:
                            raise Exception("S3 Upload Failed")

                        DailyWorkProgressImage.objects.create(
                            dtl_key=dtl,
                            image_url=s3_url,
                            caption=image.get('caption'),
                            created_by=user,
                            client_id_id=clientID
                        )

                    except Exception as e:
                        transaction.set_rollback(True)
                        return Response({"error": 1, "detail": f"Image upload failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # 4. Final response
            serializer = self.get_serializer(hdr)
            return Response({"error": 0, "detail": "Created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.set_rollback(True)
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, pk=None):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)

        if not isValid:
            return Response({'message': returnObj['message']}, status=returnObj['http_status'])

        try:
            hdr = DailyWorkProgressHdr.objects.get(
                key=pk, client_id=clientID, company_id=companyID
            )
        except DailyWorkProgressHdr.DoesNotExist:
            return Response({"error": 1, "detail": "DailyWorkProgressHdr does not exist"}, status=status.HTTP_404_NOT_FOUND)

        reqData = request.data
        user = UF.getCurrentSessionUser(request)

        reqData['client_id'] = clientID
        reqData['company_id'] = companyID
        reqData['updated_by'] = user

        hdr_serializer = DailyWorkProgressHdrSerializer(
            instance=hdr, data=reqData, partial=True
        )

        if not hdr_serializer.is_valid():
            return Response({"error": 1, "detail": hdr_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                hdr_serializer.save()
                processed_detail_keys = []
                processed_image_keys = []

                # S3 path
                s3_folder_path = UF.create_s3_folder_structure(
                    clientID, companyID,
                    reqData.get('project_key'),
                    reqData.get('blk_key'),
                    [reqData.get('floor_key')]
                )
                full_s3_path = f"{s3_folder_path}/daily_progress"

                images_to_delete = DailyWorkProgressImage.objects.filter(
                    dtl_key__hdr_key=hdr.key
                ).exclude(key__in=[img_data.get("key") for detail_data in reqData.get("details", []) for img_data in detail_data.get("images", []) if img_data.get("key")])

                for image in images_to_delete:
                    try:
                        s3_result = UF.delete_file_from_s3(image.image_url)
                        if not s3_result.get("success"):
                            print(f"Failed to delete S3 file {image.image_url}: {s3_result.get('error')}")

                    except Exception as e:
                        print('Error occured while deleting s3 image: ', str(e))
                        return Response({'error' : 'Error occured while trying to delete images'}, status=status.HTTP_404_NOT_FOUND)
                    

                for detail_data in reqData.get("details", []):
                    detail_key = detail_data.get("key")
                    detail_data['hdr_key'] = hdr.key
                    detail_data['updated_by'] = user
                    detail_data['client_id'] = clientID

                    if detail_key:
                        try:
                            dtl_instance = DailyWorkProgressDtl.objects.get(
                                pk=detail_key)
                            dtl_serializer = DailyWorkProgressDtlSerializer(
                                instance=dtl_instance, data=detail_data, partial=True
                            )
                        except DailyWorkProgressDtl.DoesNotExist:
                            return Response({"error": 1, "detail": f"Detail with key {detail_key} not found"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        detail_data['created_by'] = user
                        dtl_serializer = DailyWorkProgressDtlSerializer(
                            data=detail_data)

                    if not dtl_serializer.is_valid():
                        return Response({"error": 1, "detail": dtl_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    dtl_serializer.save()
                    dtl_instance = dtl_serializer.instance
                    processed_detail_keys.append(dtl_instance.key)

                    # Process images for this detail
                    for img_data in detail_data.get("images", []):
                        img_key = img_data.get("key")
                        base64_img = img_data.get("image_url")

                        if img_key:
                            try:
                                img_instance = DailyWorkProgressImage.objects.get(
                                    pk=img_key)
                                img_serializer = DailyWorkProgressImageSerializer(
                                    instance=img_instance, data=img_data, partial=True
                                )
                            except DailyWorkProgressImage.DoesNotExist:
                                continue  # skip invalid keys
                        else:
                            if base64_img:
                                try:
                                    header, base64_data = base64_img.split(
                                        ',', 1)
                                    decoded_file = base64.b64decode(
                                        base64_data)
                                    file_like = io.BytesIO(decoded_file)

                                    file_name = f"{uuid.uuid4()}.jpg"
                                    s3_path = f"{full_s3_path}/{file_name}"

                                    s3_url = UF.upload_file_to_s3(
                                        s3_path, file_like)
                                    if not s3_url:
                                        raise Exception("S3 Upload Failed")

                                    img_data['image_url'] = s3_url
                                    img_data['dtl_key'] = dtl_instance.key
                                    img_data['created_by'] = user
                                    img_data['client_id'] = clientID

                                    img_serializer = DailyWorkProgressImageSerializer(
                                        data=img_data)
                                except Exception as e:
                                    transaction.set_rollback(True)
                                    return Response({"error": 1, "detail": f"Image upload failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                continue

                        if img_serializer.is_valid():
                            img_serializer.save()
                            processed_image_keys.append(
                                img_serializer.instance.key)
                        else:
                            return Response({"error": 1, "detail": img_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                # Delete removed details
                DailyWorkProgressDtl.objects.filter(hdr_key=hdr.key).exclude(
                    key__in=processed_detail_keys).delete()

                # Delete removed images
                DailyWorkProgressImage.objects.filter(dtl_key__hdr_key=hdr.key).exclude(
                    key__in=processed_image_keys).delete()

                return Response({
                    "error": 0,
                    "detail": "Daily Work Progress updated successfully",
                    "data": hdr_serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            transaction.set_rollback(True)
            return Response({"error": 1, "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
