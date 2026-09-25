from rest_framework import serializers
from users.models import AppUser, AppRole, AppPermission, AppRolePermission, UserSettings, AppUsersRole, AppUserCompany
from buildiq.super_serializer import DynamicFieldsModelSerializer


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    user_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    is_active = serializers.BooleanField(required=True)

    role = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField(read_only=True)

    def get_company(self, user):
        if AppUserCompany.objects.filter(user=user).exists():
            appUserCompanyIns = AppUserCompany.objects.filter(user=user)
            result = []
            for usercomp in appUserCompanyIns:
                result.append({
                    "client_id": usercomp.company.client.id,
                    "id": usercomp.company.id,
                    "name": usercomp.company.name
                })
            return result
        else:
            return []

    def get_role(self, user):
        if AppUsersRole.objects.filter(user=user).exists():
            appUserRole = AppUsersRole.objects.filter(user=user)
            data = []
            for appUserRoleIns in appUserRole:
                userRole = appUserRoleIns.role
                data.append({
                    "id": userRole.id,
                    "name": userRole.role,
                    "access": [{
                        "id": acc.permission.id,
                        "name": acc.permission.permission,
                    } for acc in AppRolePermission.objects.filter(role=userRole)]
                })
            return data
        return []

    class Meta:
        model = AppUser
        fields = ('id', 'email', 'user_name', 'first_name',
                  'last_name', 'phone_number', 'profile_pic', 'is_active', 'role', 'company',)


class PermissionSerializer(serializers.ModelSerializer):
    permission = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    class Meta:
        model = AppPermission
        fields = ('id', 'permission', 'description')


class RolePermissionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = AppRolePermission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):

    access = serializers.SerializerMethodField(read_only=True)

    def get_access(self, role):
        if AppRolePermission.objects.filter(role=role).exists():
            appRolePermissions = AppRolePermission.objects.filter(role=role)
            data = []
            for appRolePermissionsIns in appRolePermissions:
                data.append({
                    "id": appRolePermissionsIns.permission.id,
                    "name": appRolePermissionsIns.permission.permission,
                })
            return data
        return []

    class Meta:
        model = AppRole
        fields = '__all__'


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'
