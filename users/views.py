from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (UserSerializer, RoleSerializer,
                          PermissionSerializer, RolePermissionSerializer,
                          UserSettingsSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from .models import (AppUser, AppRole, AppPermission,
                     AppRolePermission, AppUsersRole, Authentication,
                     UserSettings, AppUserCompany)
from buildiq.utils import UtilFunctions
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
import requests as req
from django.db.models import Count
from client.models import Company, Clientbase
import base64
from buildiq.pagenation_configs import Pagination10PerPage
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
# from rest_framework.throttling import UserRateThrottle
# import string
# import random

# class CustomUserRateThrottle(UserRateThrottle):
#     rate = '1/minute' 

class UserMeViewset(viewsets.ViewSet):
    queryset = AppUser.objects.all()

    def retrieve(self, request):
        serializer_class = UserSerializer(request.user)
        return Response(serializer_class.data)


class UserViewset(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    queryset = AppUser.objects.all()
    pagination_class = Pagination10PerPage
    serializer_class = UserSerializer

    def _get_company_ids_from_request(self, request):
        """Normalize company IDs from request; only lists are treated as assignments."""
        raw = request.data.get('company', None)
        if raw is None:
            return None
        if isinstance(raw, list):
            return [int(c) for c in raw if c is not None and str(c).strip() != '']
        if hasattr(request.data, 'getlist'):
            listed = request.data.getlist('company')
            if len(listed) > 1:
                return [int(c) for c in listed if c is not None and str(c).strip() != '']
        return None

    def _get_user_company_ids(self, user):
        return list(
            AppUserCompany.objects.filter(user=user).values_list('company_id', flat=True)
        )

    def _sync_user_companies(self, user, company_ids):
        before_ids = self._get_user_company_ids(user)
        logger.info(
            'Syncing user %s companies: incoming=%s, before=%s',
            user.id, company_ids, before_ids,
        )
        with transaction.atomic():
            AppUserCompany.objects.filter(user=user).delete()
            for comp_id in company_ids:
                companyIns = Company.objects.get(id=comp_id)
                AppUserCompany.objects.create(
                    user=user,
                    company=companyIns,
                    client_id=companyIns.client,
                )
        after_ids = self._get_user_company_ids(user)
        logger.info(
            'Synced user %s companies: after=%s',
            user.id, after_ids,
        )
        return after_ids

    def updateUserCompany(self, user, company):
        companyIns = Company.objects.get(id=company)
        appusercom = AppUserCompany(
            user=user,
            company=companyIns,
            client_id=companyIns.client
        )
        appusercom.save()

    def list(self, request):

        UF = UtilFunctions()
        isValid, returnObj, clientID, companyID = UF.getClientInfo(request)
        if not isValid:
            return Response(returnObj['message'], status=returnObj['http_status'])

        queryset = AppUser.objects.filter(
            id__in=AppUserCompany.objects.filter(
                company=companyID
            ).values_list("user_id", flat=True)
        ).order_by('-id')

        # Handle without pagination
        if request.GET.get("without_pagination") and int(request.GET.get("without_pagination")) == 1:
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)

        # Paginated response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

        # if AppUserCompany.objects.filter(company=companyID).exists():
        #     queryset = AppUser.objects.filter(
        #         id__in=AppUserCompany.objects.filter(
        #             company=companyID
        #         ).values_list("user_id")
        #     )
        #     serializer_class = UserSerializer(queryset, many=True)
        #     return Response(serializer_class.data)
        # else:
        #     return Response([])

    def update(self, request, pk=None):
        userIns = get_object_or_404(self.queryset, pk=pk)
        serializer = UserSerializer(
            userIns, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                userRoleId = request.data.get("role", False)
                if userRoleId:
                    if AppUsersRole.objects.filter(user=userIns).exists():
                        AppUsersRole.objects.filter(user=userIns).delete()
                    userRole = AppUsersRole(
                        user=userIns, role=AppRole.objects.get(pk=userRoleId))
                    userRole.save()

                company_ids = self._get_company_ids_from_request(request)
                if company_ids is not None:
                    if not company_ids:
                        return Response(
                            {"error": 1, "detail": "At least one company must be selected"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    self._sync_user_companies(userIns, company_ids)

                userIns.refresh_from_db()
                response_serializer = UserSerializer(userIns)
                return Response(
                    {
                        "error": 0,
                        "detail": "User Updated Successfully",
                        "data": response_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": 1, "detail": f"Error In User PUT Request: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": 1, "detail": f"Error In User PUT Request: {serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        post = get_object_or_404(self.queryset, pk=pk)
        serializer_class = UserSerializer(post)
        return Response(serializer_class.data)

    def delete(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        user.delete()
        return Response("deleted success")

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        UF = UtilFunctions()
        if serializer.is_valid():
            try:
                error, errorObj = UF.validateUserPostData(request)
                if error:
                    return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
                user = serializer.save()
                if user:
                    userRole = request.data.get('role', False)
                    if userRole:
                        userRole = AppUsersRole(
                            user=user, role=AppRole.objects.get(pk=userRole))
                        userRole.save()
                    company_ids = self._get_company_ids_from_request(request)
                    if company_ids is not None:
                        if not company_ids:
                            return Response(
                                {"error": 1, "message": "At least one company must be selected"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        self._sync_user_companies(user, company_ids)
                    user.refresh_from_db()
                    response_serializer = UserSerializer(user)
                    return Response(
                        {"message": "User Added Successfully", "user": response_serializer.data},
                        status=status.HTTP_201_CREATED,
                    )
            except Exception as e:
                return Response({"error": 1, "message": f"Something Went Wrong: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            firstErrorKey = list(serializer.errors.keys())[0]
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = AppRole.objects.all()
    UF = UtilFunctions()

    def list(self, request):
        serializer_class = RoleSerializer(self.queryset.all(), many=True)
        return Response(serializer_class.data)

    def retrieve(self, request, pk=None):
        role = get_object_or_404(self.queryset, pk=pk)
        serializer_class = RoleSerializer(role)
        return Response(serializer_class.data)

    def update(self, request, pk=None):
        roleIns = get_object_or_404(self.queryset, pk=pk)

        roleIns.role = request.data.get('role')
        roleIns.is_role_active = request.data.get('is_role_active')
        roleIns.role_description = request.data.get('role_description')
        roleIns.save()

        incomingAccessList = request.data.get('access', [])
        insertedAccessList = []

        # delete previous access
        AppRolePermission.objects.filter(role=roleIns).delete()

        roleName = request.data.get('role')
        for accessID in request.data.get("access", []):
            if AppRolePermission.objects.checkSingleRolePermissionExists(pk, accessID):
                continue

            serializer = RolePermissionSerializer(
                data={"role": pk, "permission": accessID, 'description': roleName})

            if serializer.is_valid():
                try:
                    role = serializer.save()
                except:
                    errorObj = self.UF.get_Error_Object(
                        "Something Went Wrong")
                    return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        finalData = RoleSerializer(
            AppRole.objects.get(id=pk)).data
        return Response(finalData, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        role = get_object_or_404(self.queryset, pk=pk)
        role.delete()
        return Response("deleted success")

    def create(self, request):
        serializer = RoleSerializer(data=request.data)
        UF = UtilFunctions()
        if serializer.is_valid():
            try:
                role = serializer.save()
                if role:
                    json = serializer.data
                    roleId = serializer.data.get("id")
                    roleName = serializer.data.get("role")
                    for accessID in request.data.get("access", []):
                        if AppRolePermission.objects.checkSingleRolePermissionExists(roleId, accessID):
                            continue
                        serializer = RolePermissionSerializer(
                            data={"role": roleId, "permission": accessID, 'description': roleName})
                        if serializer.is_valid():
                            try:
                                role = serializer.save()
                            except:
                                errorObj = UF.get_Error_Object(
                                    "Something Went Wrong")
                                return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
                    finalData = RoleSerializer(
                        AppRole.objects.filter(id=roleId), many=True).data
                    return Response(finalData, status=status.HTTP_201_CREATED)
            except:
                errorObj = UF.get_Error_Object("Role Already There")
                return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionsViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = AppPermission.objects.all()

    def list(self, request):
        serializer_class = PermissionSerializer(self.queryset.all(), many=True)
        return Response(serializer_class.data)

    def create(self, request):
        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                role = serializer.save()
                if role:
                    json = serializer.data
                    return Response(json, status=status.HTTP_201_CREATED)
            except:
                return Response({"detail": "Permission Already There"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RolePermissionViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = AppRolePermission.objects.all()

    def list(self, request):
        roles = AppRole.objects.all().values('role', 'id')
        group_by_value = {}
        for role in roles:
            if not AppRolePermission.objects.filter(role_id=role['id']).exists():
                continue
            permissionList = []
            for permission in AppRolePermission.objects.filter(role_id=role['id']).values('permission_id'):
                permissionList.append(PermissionSerializer(AppPermission.objects.get(
                    pk=permission['permission_id'])).data['permission'])
            group_by_value[role['id']] = {
                "name": role['role'], "permissions": permissionList}

        return Response(group_by_value)

    def create(self, request):
        UF = UtilFunctions()
        permissionIds = request.data.get('permission', [])
        roleId = request.data.get('role', 0)
        description = request.data.get('description', '')

        if not description:
            errorObj = UF.get_Error_Object("Description Must Be Filled")
            return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)

        for pID in permissionIds:
            if AppRolePermission.objects.checkRolePermissionExists(roleId, pID):
                continue

            serializer = RolePermissionSerializer(
                data={"role": roleId, "permission": pID, 'description': description})
            if serializer.is_valid():
                try:
                    role = serializer.save()
                except:
                    errorObj = UF.get_Error_Object("Something Went Wrong")
                    return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Role Mapped To Selected Permissions"}, status=status.HTTP_201_CREATED)


class AuthenticationVIEW(APIView):
    permission_classes = [AllowAny, ]
    http_method_names = ['get', 'head', 'post']
    # throttle_classes = [CustomUserRateThrottle]

    def get(self, request, *args, **kwargs):
        UF = UtilFunctions()
        email = request.GET.get('email')
        error, errorObj = UF.validateOTPGETData(email)
        if error:
            return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)

        try:
            # session = ''.join(random.choices(string.ascii_uppercase +
            #                                  string.digits, k=28))
            # return Response({"Status": "Success", "message": "If the number is valid, you'll receive an OTP shortly.", "Details": session}, status=status.HTTP_202_ACCEPTED)
            result  = UF.send_otp(email)
            if result["error"]==0:
                authInstance = Authentication(
                    email=email, session=result["sessionID"])
                authInstance.save()
                return Response({"Status": "Success", "message": result["message"], "Details": result["sessionID"]}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"error":1, "message": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": error, "message": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        UF = UtilFunctions()
        email = request.data.get("email")
        otpSID = request.data.get("session_id")
        otp = request.data.get("otp")
        error, errorObj = UF.validateOTPPOSTData(email, otpSID, otp)
        if error:
            return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
        
        res = {
            "Status": "failed",
        }
        result = UF.verify_otp(email=email, otp=otp)
        
        if result["error"] == 1:
            return Response(result["message"], status=status.HTTP_400_BAD_REQUEST)
        
        if Authentication.objects.filter(email=email, session=otpSID).exists():
            res["Status"] = "Success"

        authInstance = Authentication.objects.get(
            email=email, session=otpSID
        )
        authInstance.otp = otp
        authInstance.status = res["Status"].lower()
        authInstance.save()

        if res.get('Status') == 'Success':
            userInstance = AppUser.objects.get(email=email)

            refresh = RefreshToken.for_user(userInstance)
            res['user'] = UserSerializer(userInstance).data
            res['auth_token'] = {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
            res.update(UF.getCompanyInfo(userInstance))

            return Response(res, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     errorObj = UF.get_Error_Object("Invalid Request")
        #     return Response(errorObj, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny, ]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserSettingsViewset(viewsets.ViewSet):
    # permission_classes = [AllowAny, ]
    queryset = UserSettings.objects.all()

    def list(self, request):
        UF = UtilFunctions()
        userid = UF.userIdFromRequest(request, "FROM_QPARAM")
        serializer_class = UserSettingsSerializer(
            UserSettings.objects.filter(user=userid), many=True)
        return Response(serializer_class.data)

    def create(self, request):
        UF = UtilFunctions()
        userid = UF.userIdFromRequest(request, "FROM_BODY")

        if not (userid and len(request.data.get('settings', []))):
            msg = "User setting missing"
            return Response({"error": 0, "message": msg}, status=status.HTTP_400_BAD_REQUEST)

        # Deleting all user settings
        UserSettings.objects.filter(user=userid).delete()

        settingData = []
        for setting in request.data.get('settings', []):
            setting['user'] = userid
            serializer = UserSettingsSerializer(data=setting)
            if serializer.is_valid():
                try:
                    serializer.save()
                    settingData.append(serializer.data)
                except:
                    errorObj = UF.get_Error_Object("Something Went Wrong")
                    return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)

        if len(settingData):
            msg = "User Setting Modified Successfully"
            return Response({"error": 0, "message": msg, "data": settingData}, status=status.HTTP_201_CREATED)
        else:
            errorObj = UF.get_Error_Object(
                "Something Went Wrong. Check the request param")
            return Response(errorObj, status=status.HTTP_400_BAD_REQUEST)
        msg = "User setting missing"
        return Response({"error": 0, "message": msg}, status=status.HTTP_400_BAD_REQUEST)
