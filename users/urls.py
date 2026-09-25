from django.urls import path
from .views import (UserViewset, RoleViewset, PermissionsViewset,
                    RolePermissionViewset, BlacklistTokenUpdateView, AuthenticationVIEW, UserMeViewset,
                    UserSettingsViewset)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from buildiq.utils import ENDPOINT_METHODS_DICT

app_name = 'users'

GET_POST = ENDPOINT_METHODS_DICT['GET_POST']
RETRIVE = ENDPOINT_METHODS_DICT['RETRIVE']
RETRIVE_UPDATE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE']
RETRIVE_UPDATE_DELETE = ENDPOINT_METHODS_DICT['RETRIVE_UPDATE_DELETE']


urlpatterns = [
    #     path('useradd/', UserCreate.as_view(), name="create_user"),


    path('user/settings/',
         UserSettingsViewset.as_view(GET_POST), name="app_users"),

    path('user/',
         UserViewset.as_view(GET_POST), name="app_users"),

    path('user/<int:pk>',
         UserViewset.as_view(RETRIVE_UPDATE), name="list_user"),

    path('me/',
         UserMeViewset.as_view(RETRIVE), name="app_users_me"),

    path('role/',
         RoleViewset.as_view(GET_POST), name="app_roles"),

    path('role/<int:pk>',
         RoleViewset.as_view(RETRIVE_UPDATE_DELETE), name="app_role"),

    path('permission/',
         PermissionsViewset.as_view(GET_POST), name="app_permissions"),

    path('role_permission/',
         RolePermissionViewset.as_view(GET_POST), name="role_permission_mapping"),

    path('otp/', AuthenticationVIEW.as_view(), name='authentication'),

    path('logout/blacklist/', BlacklistTokenUpdateView.as_view(), name='blacklist'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
