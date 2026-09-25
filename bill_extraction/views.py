from django.conf import settings
from rest_framework import status
from buildiq.utils import UtilFunctions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from buildiq.services.file_processing import FileProcessingService
from .sockets import sessions
from buildiq.services.vector_db_helper import VectorDBUtils


class CheckSessionStatusView(APIView):
    def get(self, request, session_id):
        is_active = session_id in sessions or any(
            s["mobile_session_id"] == session_id for s in sessions.values())

        return Response({"session_id": session_id, "is_active": is_active}, status=status.HTTP_200_OK)


class AllSessionStatusView(APIView):
    def get(self, request):
        return Response({"sessions": sessions}, status=status.HTTP_200_OK)


class GenerateQRCodeView(APIView):
    def get(self, request, session_id):
        UF = UtilFunctions()
        frontend_url = settings.FRONTEND_URL
        data = f"{frontend_url}/mobile-upload?sessionId={session_id}"

        result = UF.generate_qr_code(data)

        if not result["success"]:
            return Response(
                {"error": result["error"], "type": result["type"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return result["response"]


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, session_id):
        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        uploaded_file = request.FILES.get("file")
        file_path = UF.create_s3_folder_structure(client_id=clientID,company_id=companyID)
        updated_file_path   = file_path + '/UploadedBills/' + session_id

        result = UF.upload_file_to_s3(updated_file_path, uploaded_file)

        if not result:
            return Response(
                {"error": "Error Occured while uploading file to S3"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "File uploaded successfully!",
                "file_url": result},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, session_id):
        UF = UtilFunctions()
        file_name = request.GET.get("file_name")
        result = UF.delete_file_from_s3(file_name)

        if not result["success"]:
            return Response(
                {"error": result["error"], "type": result["type"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": result["message"]}, status=status.HTTP_200_OK)


class FileProcessingView(APIView):
    parser_classes = (MultiPartParser,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_service = FileProcessingService()
        self.util = UtilFunctions()

    def post(self, request):
        file = request.data["file"]
        required_fields = ["session_id", "uploaded_from", "file_type"]
        missing_fields = [
            field for field in required_fields if field not in request.data]

        print("File:", file)

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        if missing_fields:
            return Response({"error": f"{', '.join(missing_fields)} is required"}, status=status.HTTP_400_BAD_REQUEST)

        session_id = request.data["session_id"]
        uploaded_from = request.data["uploaded_from"]
        file_type = request.data["file_type"]

        print("Uploaded from:", uploaded_from)
        print("file_type:", file_type)
        print("session_id:", session_id)

        result = self.file_service.process_file(file, file_type, uploaded_from)

        if result.get("success"):
            return Response({"success": True, "data": result["data"]}, status=status.HTTP_200_OK)

        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class UpdateItemInVectorDBView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vector_db = VectorDBUtils()

    def post(self, request):
        matched_items = request.data.get("matched_items")

        if not matched_items or not isinstance(matched_items, list):
            return Response({"error": "matched_items must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        responses = []

        for item in matched_items:
            if not item['scanned_item_name'] or not item['db_item_name']:
                responses.append({
                    "item": item['scanned_item_name'],
                    "success": False,
                    "error": "Both scanned_item_name and db_item_name are required.",
                })
                continue

            try:
                result = self.vector_db.get_or_create_similar_item_vector(
                    item['db_item_name'], item['scanned_item_name'], item['item_key'])

                if result.get("success"):
                    responses.append({
                        "item_key": item['item_key'],
                        "item": item['db_item_name'],
                        "success": True,
                        "message": "Item updated successfully.",
                        "matched_item_descr": item['scanned_item_name'],
                        "quantity": item['quantity'],
                        "total_price": item['total_price'],
                    })
                else:
                    responses.append({
                        "item": item['db_item_name'],
                        "success": False,
                        "error": result.get("error"),
                    })

            except Exception as e:
                responses.append({
                    "item": item['db_item_name'],
                    "success": False,
                    "error": str(e),
                })

        return Response({"results": responses}, status=status.HTTP_200_OK)
